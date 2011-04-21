Name:           ossxp-linux
Version:        5
Release:        1
Summary:        Packages for Linux customization

Group:          System Environment/Base 
License:        GPL 
URL:            http://update.ossxp.com/centos

Source0:        http://update.ossxp.com/centos/RPM-GPG-KEY-OSSXP
Source1:        GPL
Source2:        ossxp.repo

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:     noarch
#Requires:      redhat-release >=  %{version} 
#Conflicts:     fedora-release

%description
This package contains the configuration for OSSXP CentOS/RHEL repository
GPG key as well as configuration for yum.

%prep
%setup -q  -c -T
install -pm 644 %{SOURCE0} .
install -pm 644 %{SOURCE1} .
install -pm 644 %{SOURCE2} .

%build


%install
rm -rf $RPM_BUILD_ROOT

#GPG Key
install -Dpm 644 %{SOURCE0} \
    $RPM_BUILD_ROOT%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-OSSXP

# yum
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d
install -pm 644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d

%clean
rm -rf $RPM_BUILD_ROOT

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
