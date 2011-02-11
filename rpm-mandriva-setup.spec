%if %{?distsuffix:0}%{?!distsuffix:1}
%define distsuffix mdv
%endif

%if %{?mkrel:0}%{?!mkrel:1}
%define mkrel(c:) %{-c: 0.%{-c*}.}%{1}%{?distsuffix:%distsuffix}%{?!distsuffix:mdv}%{?mandriva_release:%mandriva_release}%{?subrel:.%subrel}
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
Version:	1.116
Release:	%mkrel 1
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
Conflicts:	rpm <= 1:4.4.2.3-0.rc1.1mdv2008.1
%endif

%description
The Mandriva rpm configuration and scripts.

%package	build
Group:		System/Configuration/Packaging
Summary:	The Mandriva rpm configuration and scripts to build rpms
Requires:	rpm-manbo-setup-build >= 0.4
Requires:	spec-helper >= 0.6-5mdk
Requires:	multiarch-utils >= 1.0.3
Requires:	pkgconfig
Requires:	python-pkg-resources
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
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

mkdir -p %buildroot%{_sysconfdir}/rpm/macros.d

mv %buildroot%_prefix/lib/rpm/mandriva/macros %buildroot%{_sysconfdir}/rpm/macros.d/20common.macros
mv %buildroot%{_sysconfdir}/rpm/macros.d/{build.macros,20build.macros}


%if %have_emacsmodespec
# spec mode for emacs
install -d $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/
install -m644 rpm-spec-mode.el $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/

install -d $RPM_BUILD_ROOT%{_sysconfdir}/emacs/site-start.d
cat <<EOF >$RPM_BUILD_ROOT%{_sysconfdir}/emacs/site-start.d/%{name}.el
(setq auto-mode-alist (cons '("\\\\.spec$" . rpm-spec-mode) auto-mode-alist))
(autoload 'rpm-spec-mode "rpm-spec-mode" "RPM spec mode (mandrakized)." t)
EOF
%endif

# workaround to fix build with rpm-mandriva-setup 1.96
touch debugfiles.list
%check
make test

%clean
rm -rf $RPM_BUILD_ROOT

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
%dir %{_sysconfdir}/rpm/macros.d
%{_sysconfdir}/rpm/macros.d/20common.macros

%files build
%defattr(-,root,root)
%doc NEWS ChangeLog
%{_sysconfdir}/rpm/macros.d/20build.macros
%{_prefix}/lib/rpm/mandriva/*
%if %have_emacsmodespec
%{_datadir}/emacs/site-lisp/rpm-spec-mode.el
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
%endif
