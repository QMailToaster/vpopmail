Name:		vpopmail
Summary:	Vpopmail for QMail Toaster
Version:	5.4.33
Release:	0%{?dist}
License:	GPL
Group:		Networking/Other
URL:		http://www.inter7.com/%{name}
Source0:	http://downloads.sourceforge.net/project/vpopmail/vpopmail-stable/5.4.33/%{name}-%{version}.tar.gz
Source1:	vpopmail.mysql
Patch0:		vpopmail-toaster-5.4.33.patch
Patch1:		vpopmail-build-no-root-5.4.33.patch
Patch2:		vpopmail-build-no-qmail-5.4.33.patch
Patch3:		vpopmail-build-devel-5.4.33.patch
BuildRequires:	automake
BuildRequires:	mysql-devel >= 5.0.22
Requires:	mysql >= 5.0.22
Obsoletes:	vpopmail-toaster
Obsoletes:	vpopmail-toaster-doc
Conflicts:      set-toaster, checkpassword
BuildRoot:      %{_topdir}/BUILDROOT/%{name}-%{version}-%{release}.%{_arch}

%define debug_package %{nil}
%define vdir          /home/vpopmail

#-------------------------------------------------------------------------------
%description
#-------------------------------------------------------------------------------
vpopmail (vchkpw)  is a collection  of programs  and a library to automate
the creation and maintence of virtual domain email for qmail installations
using either a single UID/GID, or any valid  UID/GID in /etc/passwd with a
home directory. All the  features  are  provided  in the library for other
applications which need to maintain virtual domain email accounts.

It supports named or IP based domains.  It works with vqadmin, qmailadmin,
vqregister, sqwebmail, and dovecot.

It supports MySQL,  Sybase,  Oracle,  LDAP,  and  file-based (DJB constant
database) authentication.

It handles 10 to 10 million users, and over 500K domains.

 
           vpopmail 5.4.33
            Current settings
---------------------------------------

vpopmail directory = /home/vpopmail
               uid = 89
               gid = 89
     roaming users = OFF --disable-roaming-users   (default)
 password learning = OFF --disable-learn-passwords (default)
     md5 passwords = ON  --enable-md5-passwords    (default)
      file locking = ON  --enable-file-locking     (default)
vdelivermail fsync = OFF --disable-file-sync       (default)
     make seekable = ON  --enable-make-seekable    (default)
      clear passwd = ON  --enable-clear-passwd     (default)
 user dir hashing  = OFF --disable-users-big-dir
address extensions = ON  --enable-qmail-ext
          ip alias = OFF --disable-ip-alias-domains (default)
       auth module = mysql --enable-auth-module=mysql
 mysql replication = OFF --disable-mysql-replication (default)
       sql logging = OFF --disable-sql-logging       (default)
      mysql limits = OFF --disable-mysql-limits      (default)
      MySQL valias = ON  --enable-valias
          auth inc = -I/usr/include/mysql
          auth lib = -L/usr/lib64/mysql  -lmysqlclient -lz -lm
  system passwords = OFF --disable-passwd (default)
        pop syslog = log success and errors including passwords
                         --enable-logging=v
      auth logging = ON  --enable-auth-logging (default)
one domain per SQL table = --disable-many-domains

%package -n %{name}-devel
Summary:	vpopmail development headers and libs
Group:		System/Servers
%description -n %{name}-devel
Headers and libs for building packages which use vpopmail.

#-------------------------------------------------------------------------------
%prep
#-------------------------------------------------------------------------------
%setup -q

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

#-------------------------------------------------------------------------------
%build
#-------------------------------------------------------------------------------
autoreconf
%{__automake}
%{__autoconf}
./configure --prefix=%{vdir} \
	--enable-vpopuser=vpopmail \
	--enable-vpopgroup=vchkpw \
        --enable-libdir=%{_libdir}/mysql \
	--disable-roaming-users \
	--enable-tcprules-prog=/usr/bin/tcprules \
	--enable-tcpserver-file=/etc/tcprules.d/tcp.smtp \
	--enable-make-seekable \
	--enable-clear-passwd \
	--disable-users-big-dir \
	--enable-qmail-ext \
	--disable-ip-alias-domains \
	--enable-auth-module=mysql \
	--disable-passwd \
	--enable-logging=v \
	--enable-log-name=vpopmail \
	--disable-mysql-limits \
	--enable-valias \
	--disable-many-domains \
	--enable-non-root-build
make

#-------------------------------------------------------------------------------
%install
#-------------------------------------------------------------------------------
%{__rm} -rf %{buildroot}
make DESTDIR=%{buildroot} install-strip

# Set defaults for vpopmail mysql
#-------------------------------------------------------------------------------
%{__mv} %{buildroot}%{vdir}/etc/vpopmail.mysql \
        %{buildroot}%{vdir}/etc/vpopmail.mysql.dist
%{__install} -p %{_sourcedir}/vpopmail.mysql %{buildroot}%{vdir}/etc/.

# Install domain quota messages
#-------------------------------------------------------------------------------
# install overquota.msg  %{buildroot}%{vdir}/domains
%{__install} quotawarn.msg %{buildroot}%{vdir}/domains/.quotawarn.msg

# move devel files to their normal places for the -devel package
%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name} \
             %{buildroot}%{_includedir}/%{name} \
             %{buildroot}%{_libdir}/%{name}
%{__mv} %{buildroot}%{vdir}/etc/*_deps %{buildroot}%{_sysconfdir}/%{name}/.

# shubes 11/18/2013 - This is a hack.
# TODO: Need to get proper object library handling implemented for vpopmail
%ifarch x86_64
  sed -i 's|/usr/lib/|/usr/lib64/|' %{buildroot}%{_sysconfdir}/%{name}/lib_deps
%endif

%{__mv} %{buildroot}%{vdir}/include/*  %{buildroot}%{_includedir}/%{name}/.
%{__mv} %{buildroot}%{vdir}/lib/*      %{buildroot}%{_libdir}/%{name}/.
rmdir %{buildroot}%{vdir}/include \
      %{buildroot}%{vdir}/lib

#-------------------------------------------------------------------------------
%clean
#-------------------------------------------------------------------------------
%{__rm} -rf %{buildroot}

#-------------------------------------------------------------------------------
%pre
#-------------------------------------------------------------------------------
# Create group and user if they don't exist
#-------------------------------------------------------------------------------
if [ -z "`/usr/bin/id -g vchkpw 2>/dev/null`" ]; then
  /usr/sbin/groupadd -g 89 -r vchkpw 2>&1 || :
fi

if [ -z "`/usr/bin/id -u vpopmail 2>/dev/null`" ]; then
  /usr/sbin/useradd -u 89 -r -M -d %{vdir}  -s /sbin/nologin -c "Vpopmail User" -g vchkpw vpopmail 2>&1 || :
fi

#-------------------------------------------------------------------------------
%preun
#-------------------------------------------------------------------------------
if [ "$1" = 0 ]; then
  userdel vpopmail 2> /dev/null
  groupdel vchkpw 2> /dev/null
fi

#-------------------------------------------------------------------------------
%post
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
%files
#-------------------------------------------------------------------------------
%defattr (-,vpopmail,vchkpw)
%attr(0700,vpopmail,vchkpw) %dir %{vdir}
%attr(0755,vpopmail,vchkpw) %dir %{vdir}/bin
%attr(0755,vpopmail,vchkpw) %dir %{vdir}/etc
%attr(0700,vpopmail,vchkpw) %dir %{vdir}/domains
#%attr(0755,vpopmail,vchkpw) %dir %{vdir}/include
#%attr(0755,vpopmail,vchkpw) %dir %{vdir}/lib

%attr(0751,vpopmail,vchkpw) %{vdir}/bin/*
%attr(0644,vpopmail,vchkpw) %{vdir}/domains/.quotawarn.msg
#%attr(0644,vpopmail,vchkpw) %{vdir}/domains/.overquota.msg
%attr(0644,vpopmail,vchkpw) %{vdir}/etc/vusagec.conf
%attr(0644,vpopmail,vchkpw) %config(noreplace) %{vdir}/etc/vlimits.default
%attr(0644,vpopmail,vchkpw) %config(noreplace) %{vdir}/etc/vpopmail.mysql
%attr(0644,vpopmail,vchkpw) %{vdir}/etc/vpopmail.mysql.dist

%attr(0755,vpopmail,vchkpw) %dir %{vdir}/doc
%attr(0755,vpopmail,vchkpw) %dir %{vdir}/doc/doc_html
%attr(0755,vpopmail,vchkpw) %dir %{vdir}/doc/man_html
%attr(0444,vpopmail,vchkpw) %{vdir}/doc/doc_html/*
%attr(0444,vpopmail,vchkpw) %{vdir}/doc/man_html/*

#-------------------------------------------------------------------------------
%files -n %{name}-devel
#-------------------------------------------------------------------------------
%defattr (-,root,root)
%attr(0755,root,root) %dir %{_sysconfdir}/%{name}
%attr(0755,root,root) %dir %{_includedir}/%{name}
%attr(0755,root,root) %dir %{_libdir}/%{name}
%attr(0644,root,root)      %{_sysconfdir}/%{name}/*_deps
%attr(0644,root,root)      %{_includedir}/%{name}/*
%attr(0644,root,root)      %{_libdir}/%{name}/*

#-------------------------------------------------------------------------------
%changelog
#-------------------------------------------------------------------------------
* Fri Nov 15 2013 Eric Shubert <eric@datamatters.us> 5.4.33-0.qt
- Migrated to github
- Removed -toaster designation
- Created vpopmail-build-no-root patch. Thanks go to Johannes Weberhofer.
- Added CentOS 6 support
- Removed unsupported cruft
- Created separate -devel package
* Wed Aug  1 2012 Eric Shubert <eric@datamatters.us> 5.4.33-1.4.0
- Bumped version to 1.4.0
* Fri Feb 25 2011 Jake Vickers <jake@qmailtoaster.com> 5.4.33-1.3.8
- Updated vpopmail to 5.4.33
- Re-diffed the qmailtoaster patch for 5.4.33
* Fri Jun 12 2009 Jake Vickers <jake@qmailtoaster.com> 5.4.17-1.3.7
- Added Fedora 11 support
- Added Fedora 11 x86_64 support
* Tue Jun 02 2009 Jake Vickers <jake@qmailtoaster.com> 5.4.17-1.3.7
- Added Mandriva 2009 support
* Wed Apr 22 2009 Jake Vickers <jake@qmailtoaster.com> 5.4.17-1.3.6
- Added Fedora 9 x86_64 and Fedora 10 x86_64 support
* Fri Feb 13 2009 Jake Vickers <jake@qmailtoaster.com> 5.4.17-1.3.5
- Added Suse 11.1 support
* Sun Feb 08 2009 Jake Vickers <jake@qmailtoaster.com> 5.4.17-1.3.5
- Added Fedora 9 and 10 support
* Sat Apr 14 2007 Nick Hemmesch <nick@qmailtoaster.com> 5.4.17-1.3.4
- Update to vpopmail-5.4.17
- Added CentOS 5 i386 support
- Added CentOS 5 x86_64 support
* Wed Nov 01 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 5.4.13-1.3.3
- Added Fedora Core 6 support
* Fri Jul 14 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 5.4.13-1.3.2
- Added vpopmail-5.4.13-mysql patch, fixes mysql's gone away error
* Mon Jun 05 2006 Nick Hemmesch <nick@ndhsoft.com> 5.4.13-1.3.1
- Add SuSE 10.1 support
* Sat May 13 2006 Nick Hemmesch <nick@ndhsoft.com> 5.4.13-1.2.12
- Add Fedora Core 5 support
* Fri Apr 28 2006 Nick Hemmesch <nick@ndhsoft.com> 5.4.13-1.2.11
- Update to vpopmail-5.4.13
* Sun Nov 20 2005 Nick Hemmesch <nick@ndhsoft.com> 5.4.10-1.2.10
- Add SuSE 10.0 and Mandriva 2006.0 support
* Fri Oct 14 2005 Nick Hemmesch <nick@ndhsoft.com> 5.4.10-1.2.9
- Add Fedora Core 4 x86_64 support
- Make vlimits.default and vpopmail.mysql no replace config files
* Sat Oct 01 2005 Nick Hemmesch <nick@ndhsoft.com> 5.4.10-1.2.8
- Add CentOS 4 x86_64 support
* Wed Jun 29 2005 Nick Hemmesch <nick@ndhsoft.com> 5.4.10-1.2.7
- Add Fedora Core 4 support
* Fri Jun 03 2005 Torbjorn Turpeinen <tobbe@nyvalls.se> 5.4.10-1.2.6
- Gnu/Linux Mandrake 10.0,10.1,10.2 support
* Fri May 20 2005 Nick Hemmesch <nick@ndhsoft.com> 5.4.10-1.2.5
- Update to vpopmail-5.4.10
- Create group and user
* Tue Mar 15 2005 Nick Hemmesch <nick@ndhsoft.com> 5.4.4-1.2.4
- Add patch to build vpopmail before qmail
- Fix domainquotas
* Sun Feb 27 2005 Nick Hemmesch <nick@ndhsoft.com> 5.4.4-1.2.3
- Add Fedora Core 3 support
- Add CentOS suport
* Wed Jun 02 2004 Nick Hemmesch <nick@ndhsoft.com> 5.4.4-1.2.2
- Update to vpopmail-5.4.4
- Add Fedora Core 2 support
* Tue May 04 2004 Nick Hemmesch <nick@ndhsoft.com> 5.4.3-1.2.1
- Major rebuild of spec file
- Update to vpopmail-5.4.3
- Make rpm patch and config patch
* Sun Feb 22 2004 Nick Hemmesch <nick@ndhsoft.com> 5.3.8-1.0.12
- By popular demand, make no roaming users the default install
- Allow roaming users with "roaming" switch
* Sun Feb 15 2004 Nick Hemmesch <nick@ndhsoft.com> 5.3.8-1.0.11
- Set roaming user clear time to 15 minutes
* Mon Jan 12 2004 Nick Hemmesch <nick@ndhsoft.com> 5.3.8-1.0.10
- Fix for Trustix 2.0 by Christian Dietrich
* Sat Jan 10 2004 Nick Hemmesch <nick@ndhsoft.com> 5.3.8-1.0.9
- Add Fedora Core 1 support
- Fix Trustix 2.0 - change dependency
- Add no roaming-users as an option
- Add 15 minute expiration for roaming users
* Sun Nov 23 2003 Nick Hemmesch <nick@ndhsoft.com> 5.3.8-1.0.8
- Add Trustix 2.0
- Fix cdb function
- New patch to fix vmysql.h configure and to allow rpm build
* Sat Apr 26 2003 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-1.0.7
- Clean-ups on SPEC file: compilation banner, better gcc detects
- Detect gcc-3.2.3
- Red Hat Linux 9.0 support (nick@ndhsoft.com)
- Gnu/Linux Mandrake 9.2 support
* Wed Apr 02 2003 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-1.0.6
- Clean-ups
* Mon Mar 31 2003 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-1.0.5
- Conectiva Linux 7.0 support
* Sun Feb 15 2003 Nick Hemmesch <nick@ndhsoft.com> 5.3.8-1.0.4
- Support for Red Hat 8.0
* Wed Feb 05 2003 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-1.0.3
- Support for Red Hat 8.0 thanks to Andrew.J.Kay
* Sat Feb 01 2003 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-1.0.2
- Redo Macros to prepare supporting larger RPM OS.
  We could be able to compile (and use) packages under every RPM based
  distribution: we just need to write right requirements.
* Sat Jan 25 2003 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-1.0.1
- Added MDK 9.1 support
- Try to use gcc-3.2.1
- Added very little patch to compile with newest GLIBC
- Support dor new RPM-4.0.4
* Sat Oct 05 2002 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-0.9.2
- Soft clean-ups
* Sun Sep 29 2002 Miguel Beccari <miguel.beccari@clikka.com> 5.3.8-0.9.1
- RPM macros to detect Mandrake, RedHat, Trustix are OK again. They are
  very basic but they should work.
- Packages are named with their proper releases and bversion is from now
  part of the rpm release: we will continue upgrading safely.
* Mon Sep 23 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.8.5.3.8-1
- Rebuilded under 0.8 tree.
- Important comments translated from Italian to English.
- Written rpm rebuilds instruction at the top of the file (in english).
- Clean-ups
* Sun Sep 22 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.7.5.3.8-3
- Now cron-job works 100%!!!
* Thu Aug 29 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.7.5.3.8-2
- Deleted Mandrake Release Autodetection (creates problems)
* Fri Aug 16 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.7.5.3.8-1
- New version: 0.7 toaster.
- Better macros to detect Mandrake Release
- Minor clean-ups.
* Thu Aug 13 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.6.5.3.8-1
- New version: 0.6 toaster.
* Mon Aug 12 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.5.5.3.8-1
- Doc package is standalone (someone does not ask for man pages)
- Checks for gcc-3.2 (default compiler from now)
- New version: 0.5 toaster.
* Tue Aug 08 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.4.5.3.8-1
* Rebuild agains 0.4 toaster
- new version 5.3.8
* Thu Aug 06 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.3.5.3.5-4
- Deleted userdel and groupdel in uninstallation (safe): if the user
  wants to delete he has to do it manually (more safe)
* Wed Jul 31 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.3.5.3.5-3
- Written a patch that makes vpopmail constantly reading from sql:
  in this way tou can change on the fly sql values and we could build
  binaries version of packages (because passwords are out of the code)
* Tue Jul 30 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.3.5.3.5-2
- Now packages have got 'no sex': you can rebuild them with command line
  flags for specifics targets that are: RedHat, Trustix, and of course
  Mandrake (that is default)
* Sun Jul 28 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.2.5.3.5.1mdk
- toaster v. 0.3: now it is possible upgrading safely because of 'pversion'
  that is package version and 'version' that is toaster version
* Thu Jul 25 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.2-5.3.5.1mdk
- toaster v. 0.2: Very soft clean-ups.
* Mon Jul 22 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.1-5.3.5.4mdk
- Added useradd -r flag to create systems account. That is, an user with an
  UID  lower  than  value  of UID_MIN defined in /etc/login.defs
* Thu Jul 18 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.1-5.3.5.3mdk
- Added toaster version (we will need to mantain it too): is vtoaster 0.1
- Added cron.d files
- Added tests to make gcc to be 3.1.1
- Very soft clean-ups.
* Wed Jul 10 2002 Miguel Beccari <mighi@clikka.com> 5.3.5 2mdk
- Better dependecings (with ucspi-tcp)
- Changed the name in vpopmail-toaster beacuse we are going
  building *-toaster packages.
* Mon Jul 08 2002 Miguel Beccari <mighi@clikka.com> 5.3.5 1mdk
- First package (needs a lot of work).
- However the package is able to:
  * detect if user vpopmail exists (if not it creates)
  * detect if group exists (if not it creates)
  * apply a light patch stuff for 'make install' operations
  * read /var/qmail/control/sql and patch vmysql.h
