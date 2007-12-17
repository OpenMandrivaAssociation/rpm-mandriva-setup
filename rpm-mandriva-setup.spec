%define name rpm-mandriva-setup
%define version 1.64
%define release %mkrel 1

# This can be useful for backport, as rpm-4.2
# provides the emacs-spec mode
%define have_emacsmodespec 1
%if %mdkversion < 200600
%define have_emacsmodespec 0
%endif

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
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildRequires: rpm-devel

%description
The Mandriva rpm configuration and scripts.

%package build
Group: System/Configuration/Packaging
Summary: The Mandriva rpm configuration and scripts to build rpms
Requires: spec-helper >= 0.6-5mdk
Requires: multiarch-utils >= 1.0.3
Requires: pkgconfig
Requires: %name = %version-%release
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
%configure2_5x
%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

mkdir -p %buildroot%{_sysconfdir}/rpm/macros.d

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
%_bindir/rpmgenplatform
%dir %_prefix/lib/rpm/mandriva
%config(noreplace) %_sysconfdir/rpm/platform
%ifarch x86_64
%config(noreplace) %_sysconfdir/rpm/platform32
%endif
%_prefix/lib/rpm/mandriva/rpmrc
%_prefix/lib/rpm/mandriva/macros
%_prefix/lib/rpm/mandriva/rpmpopt
%_prefix/lib/rpm/mandriva/*-%_target_os

%dir %{_sysconfdir}/rpm/macros.d

%files build
%defattr(-,root,root)
%exclude %_prefix/lib/rpm/mandriva/rpmrc
%exclude %_prefix/lib/rpm/mandriva/macros
%exclude %_prefix/lib/rpm/mandriva/rpmpopt
%exclude %_prefix/lib/rpm/mandriva/*-%_target_os
%_prefix/lib/rpm/mandriva/*

%if %have_emacsmodespec
%{_datadir}/emacs/site-lisp/rpm-spec-mode.el
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
%endif
