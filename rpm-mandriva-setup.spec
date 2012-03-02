%if %{?distsuffix:0}%{?!distsuffix:1}
%define distsuffix mdv
%endif

# we want /etc/rpm/platform and rpmgenplatform only on rpm5.org < 5.2
%define rpmplatform %{?evr_tuple_select: 0}%{!?evr_tuple_select: %(if rpm --help | grep -q yaml; then echo 1; else echo 0; fi)}

Summary:	The Mandriva rpm configuration and scripts
Name:		rpm-mandriva-setup
Version:	1.137
Release:	1
Source0:	%{name}-%{version}.tar.xz
License:	GPLv2+
Group:		System/Configuration/Packaging
Url:		http://svn.mandriva.com/cgi-bin/viewvc.cgi/soft/rpm/rpm-setup/
# for "make test":
BuildRequires:	rpm-devel
%if !%{rpmplatform}
# older rpm do not load /usr/lib/rpm/manbo/rpmrc:
Conflicts:	rpm < 1:5.4.4-14
BuildArch:	noarch
%endif

%description
The Mandriva rpm configuration and scripts.

%package	build
Group:		System/Configuration/Packaging
Summary:	The Mandriva rpm configuration and scripts to build rpms
Requires:	spec-helper >= 0.6-5mdk
Requires:	pkgconfig
Requires:	python-pkg-resources
Requires:	perl(JSON)
Requires:	perl(YAML)
Requires:	perl(File::Basename)
Requires:	perl(File::Find)
Requires:	perl(Getopt::Long)
Requires:	perl(Pod::Usage)
Conflicts:	spec-helper <= 0.26.1

%description	build
The Mandriva rpm configuration and scripts dedicated to build rpms.

%prep
%setup -q

%build
%configure2_5x	--build=%{_build} \
%if %{rpmplatform}
		--with-rpmplatform \
%endif

%make

%install
%makeinstall_std

# spec mode for emacs
install -d %{buildroot}%{_datadir}/emacs/site-lisp/
install -m644 rpm-spec-mode.el %{buildroot}%{_datadir}/emacs/site-lisp/

install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(setq auto-mode-alist (cons '("\\\\.spec$" . rpm-spec-mode) auto-mode-alist))
(autoload 'rpm-spec-mode "rpm-spec-mode" "RPM spec mode (mandrakized)." t)
EOF

# workaround to fix build with rpm-mandriva-setup 1.96
touch debugfiles.list

%files
%if %rpmplatform
%{_bindir}/rpmgenplatform
%config(noreplace) %{_sysconfdir}/rpm/platform
%ifarch x86_64
%config(noreplace) %{_sysconfdir}/rpm/platform32
%endif
%endif

%files build
%doc NEWS ChangeLog
%dir %{_prefix}/lib/rpm/mandriva
%{_prefix}/lib/rpm/mandriva/*
%{_datadir}/emacs/site-lisp/rpm-spec-mode.el
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
