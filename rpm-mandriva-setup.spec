%define name rpm-mandriva-setup
%define version 1.90
%define release %mkrel 1

# This can be useful for backport, as rpm-4.2
# provides the emacs-spec mode
%define have_emacsmodespec 1
%if %mdkversion < 200600
%define have_emacsmodespec 0
%endif

# we want /etc/rpm/platform and rpmgenplatform only on jbj's rpm
%define rpmplatform %(if rpm --help | grep -q yaml; then echo 1; else echo 0; fi)
# jbj's doesn't use rpmrc anymore, so not using --with-only-rpmrc on it
%define only_rpmrc  %(if rpm --help | grep -q yaml; then echo 0; else echo 1; fi)

%{?_with_emacsspecmode: %define have_emacsmodespec 1}
%{?_without_emacsspecmode: %define have_emacsmodespec 0}

Summary: The Mandriva rpm configuration and scripts
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Source1: ChangeLog
License: GPL
Group: System/Configuration/Packaging
Url: http://svn.mandriva.com/cgi-bin/viewvc.cgi/soft/rpm/rpm-setup/
Requires: rpm-manbo-setup >= 0.4
BuildRoot: %{_tmppath}/%{name}-buildroot
# for "make test":
BuildRequires: rpm-manbo-setup >= 0.4
BuildRequires: rpm-devel
%if !%rpmplatform
Conflicts: rpm = 4.4.8
Conflicts: rpm = 4.4.6
# older rpm do not load /usr/lib/rpm/manbo/rpmrc:
Conflicts: rpm <= 1:4.4.2.3-0.rc1.1mdv2008.1
%endif

%description
The Mandriva rpm configuration and scripts.

%package build
Group: System/Configuration/Packaging
Summary: The Mandriva rpm configuration and scripts to build rpms
Requires: rpm-manbo-setup-build >= 0.4
Requires: spec-helper >= 0.6-5mdk
Requires: multiarch-utils >= 1.0.3
Requires: pkgconfig
Requires: %name = %version-%release
# for %mdkversion
Requires: mandriva-release
%if %have_emacsmodespec
Conflicts: rpm < 4.4.1
%endif
Conflicts: spec-helper <= 0.26.1

%description build
The Mandriva rpm configuration and scripts dedicated to build rpms.

%prep
%setup -q
cp %{_sourcedir}/ChangeLog .

%build
%configure2_5x \
%if %rpmplatform
    --with-rpmplatform \
%endif
%if %only_rpmrc
    --with-only-rpmrc \
%endif


%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

mkdir -p %buildroot%{_sysconfdir}/rpm/macros.d

%if %only_rpmrc
mv %buildroot%_prefix/lib/rpm/mandriva/macros %buildroot%{_sysconfdir}/rpm/macros.d/20common.macros
%endif
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

%check
make test

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc ChangeLog
%dir %_prefix/lib/rpm/mandriva
%if %rpmplatform
%_bindir/rpmgenplatform
%config(noreplace) %_sysconfdir/rpm/platform
%ifarch x86_64
%config(noreplace) %_sysconfdir/rpm/platform32
%endif
%endif
%if !%only_rpmrc
%_prefix/lib/rpm/mandriva/macros
%_prefix/lib/rpm/mandriva/*-%_target_os
%endif

%dir %{_sysconfdir}/rpm/macros.d
%if %only_rpmrc
%{_sysconfdir}/rpm/macros.d/20common.macros
%endif

%files build
%defattr(-,root,root)
%if !%only_rpmrc
%exclude %_prefix/lib/rpm/mandriva/macros
%exclude %_prefix/lib/rpm/mandriva/*-%_target_os
%endif
%{_sysconfdir}/rpm/macros.d/20build.macros
%_prefix/lib/rpm/mandriva/*

%if %have_emacsmodespec
%{_datadir}/emacs/site-lisp/rpm-spec-mode.el
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
%endif
