%if %{?distsuffix:0}%{?!distsuffix:1}
%define distsuffix mdv
%endif

%define mdkversion            %(perl -pe '/(\\d+)\\.(\\d)\\.?(\\d)?/; $_="$1$2".($3||0)' /etc/mandriva-release)

# This can be useful for backport, as rpm-4.2
# provides the emacs-spec mode
%define have_emacsmodespec 1
%if %mdkversion < 200600
%define have_emacsmodespec 0
%endif

# we want /etc/rpm/platform and rpmgenplatform only on rpm5.org < 5.2
%define rpmplatform %{?evr_tuple_select: 0}%{!?evr_tuple_select: %(if rpm --help | grep -q yaml; then echo 1; else echo 0; fi)}

%{?_with_emacsspecmode: %define have_emacsmodespec 1}
%{?_without_emacsspecmode: %define have_emacsmodespec 0}

Summary:	The Mandriva rpm configuration and scripts
Name:		rpm-mandriva-setup
Version:	1.135
Release:	1
Source0:	%{name}-%{version}.tar.xz
License:	GPLv2+
Group:		System/Configuration/Packaging
Url:		http://svn.mandriva.com/cgi-bin/viewvc.cgi/soft/rpm/rpm-setup/
Requires:	rpm-manbo-setup >= 0.4
BuildRoot:	%{_tmppath}/%{name}-buildroot
# for "make test":
BuildRequires:	rpm-manbo-setup >= 0.4
BuildRequires:	rpm-devel
%if !%rpmplatform
Conflicts:	rpm = 4.4.8
Conflicts:	rpm = 4.4.6
# older rpm do not load /usr/lib/rpm/manbo/rpmrc:
Conflicts:	rpm < 1:5.4.4-14
%endif

%description
The Mandriva rpm configuration and scripts.

%package	build
Group:		System/Configuration/Packaging
Summary:	The Mandriva rpm configuration and scripts to build rpms
Requires:	rpm-manbo-setup-build >= 0.4
Requires:	spec-helper >= 0.6-5mdk
Requires:	pkgconfig
Requires:	python-pkg-resources
Requires:	perl(JSON)
Requires:	perl(YAML)
Requires:	perl(File::Basename)
Requires:	perl(File::Find)
Requires:	perl(Getopt::Long)
Requires:	perl(Pod::Usage)
Requires:	%name = %version-%release
# for %mdkversion
Requires:	mandriva-release
%if %have_emacsmodespec
Conflicts:	rpm < 4.4.1
%endif
Conflicts:	spec-helper <= 0.26.1

%description	build
The Mandriva rpm configuration and scripts dedicated to build rpms.

%prep
%setup -q

%build
%configure2_5x \
%if %rpmplatform
    --with-rpmplatform \
%endif

%make

%install
rm -rf %{buildroot}
%makeinstall_std


%if %have_emacsmodespec
# spec mode for emacs
install -d %{buildroot}%{_datadir}/emacs/site-lisp/
install -m644 rpm-spec-mode.el %{buildroot}%{_datadir}/emacs/site-lisp/

install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
(setq auto-mode-alist (cons '("\\\\.spec$" . rpm-spec-mode) auto-mode-alist))
(autoload 'rpm-spec-mode "rpm-spec-mode" "RPM spec mode (mandrakized)." t)
EOF
%endif

# workaround to fix build with rpm-mandriva-setup 1.96
touch debugfiles.list
%check
make test

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%dir %{_prefix}/lib/rpm/mandriva
%if %rpmplatform
%{_bindir}/rpmgenplatform
%config(noreplace) %{_sysconfdir}/rpm/platform
%ifarch x86_64
%config(noreplace) %{_sysconfdir}/rpm/platform32
%endif
%endif

%files build
%defattr(-,root,root)
%doc NEWS ChangeLog
%{_prefix}/lib/rpm/mandriva/*
%if %have_emacsmodespec
%{_datadir}/emacs/site-lisp/rpm-spec-mode.el
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
%endif
