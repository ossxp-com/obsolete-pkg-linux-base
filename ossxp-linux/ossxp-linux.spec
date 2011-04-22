Name:           ossxp-linux
Version:        5
Release:        1
Summary:        Packages for Linux customization

Group:          System Environment/Base 
License:        GPL 
URL:            http://update.ossxp.com/centos

Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:     noarch
#Requires:      redhat-release >=  %{version} 
#Conflicts:     fedora-release

%description
This package contains the configuration for OSSXP CentOS/RHEL repository
GPG key as well as configuration for yum.

%package base
Summary: basic linux tools.
Group: System Environment/Base 

%description base
 Useful console tools, such as bzip2, p7zip, vim, ...

%package laptop
Summary: laptop utilis.
Group: System Environment/Base 
Requires: ossxp-linux-base

%description laptop
 Useful laptop utilis, such as uswsusp, acpi, ...

%package desktop-core
Summary: Desktop Environment Core (zh_CN support)
Group: System Environment/Base 
Requires: ossxp-linux-base

%description desktop-core
 X11 core with chinese support. add some utilities also.

%package desktop-light
Summary: Desktop Environment lightweight (xfce4)
Group: System Environment/Base 
Requires: ossxp-linux-desktop-core

%description desktop-light
 Light-weight Desktop Environment, using xfce4 

%package desktop-heavy
Summary: Desktop Environment heavy (KDE)
Group: System Environment/Base 
Requires: ossxp-linux-desktop-core, ossxp-linux-desktop-light

%description desktop-heavy
 Desktop Environment KDE

%package devel
Summary: Developer packages
Group: System Environment/Base 
Requires: ossxp-linux-base

%description devel
 Developer packages...

%package server
Summary: Ossxp servers
Group: System Environment/Base 
Requires: ossxp-linux-base

%description server
 Ossxp servers, such as ossxp-apache2, php5, mailman, subversion...

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT

%{__python} install.py $RPM_BUILD_ROOT

%clean
#rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc GPL
%config(noreplace) /etc/yum.repos.d/*
/etc/pki/rpm-gpg/*


%changelog
* Thu Apr 21 2011 Jiang Xin <worldhello dot net at gmail dot com>

  - add public key of Jiang Xin.

* Mon Apr 11 2011 amoblin <amoblin at ossxp.com> - 1-1
- add rsa public file.
