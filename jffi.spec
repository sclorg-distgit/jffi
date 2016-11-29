%{?scl:%scl_package jffi}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

%global cluster jnr
%global sover 1.2

Name:           %{?scl_prefix}jffi
Version:        1.2.10
Release:        1.%{baserelease}%{?dist}
Summary:        Java Foreign Function Interface

License:        LGPLv3+ or ASL 2.0
URL:            http://github.com/jnr/jffi
Source0:        https://github.com/%{cluster}/%{pkg_name}/archive/%{version}.zip
Source1:        MANIFEST.MF
Source2:        NATIVE-MANIFEST.MF
Source3:        p2.inf
Patch0:         jffi-fix-dependencies-in-build-xml.patch
Patch1:         jffi-add-built-jar-to-test-classpath.patch
Patch2:         jffi-fix-compilation-flags.patch

BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  libffi-devel
BuildRequires:  %{?scl_prefix_java_common}ant
BuildRequires:  %{?scl_prefix_java_common}ant-junit

%description
An optimized Java interface to libffi.

%package native
Summary:        %{pkg_name} JAR with native bits

%description native
This package contains %{pkg_name} JAR with native bits.

%package javadoc
Summary:        Javadoc for %{pkg_name}
BuildArch:      noarch

%description javadoc
This package contains the API documentation for %{pkg_name}.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -n %{pkg_name}-%{version} -q
cp %{SOURCE1} .
cp %{SOURCE2} .
sed -i -e's/@VERSION/%{version}/g' MANIFEST.MF
sed -i -e's/@VERSION/%{version}/g' NATIVE-MANIFEST.MF
%patch0
%patch1
%patch2

# ppc{,64} fix
# https://bugzilla.redhat.com/show_bug.cgi?id=561448#c9
sed -i.cpu -e '/m\$(MODEL)/d' jni/GNUmakefile libtest/GNUmakefile

# remove uneccessary directories
rm -rf archive/* jni/libffi/ jni/win32/ lib/CopyLibs/ lib/junit*

find ./ -name '*.jar' -exec rm -f '{}' \; 
find ./ -name '*.class' -exec rm -f '{}' \; 

build-jar-repository -s -p lib/ junit

%mvn_package 'com.github.jnr:jffi::native:' native
%mvn_file ':{*}' %{pkg_name}/@1 @1
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
# ant will produce JAR with native bits
ant jar build-native -Duse.system.libffi=1

# maven will look for JAR with native bits in archive/
cp -p dist/jffi-*-Linux.jar archive/

%mvn_build
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install

mkdir -p META-INF/
cp %{SOURCE3} META-INF/
jar umf MANIFEST.MF %{buildroot}%{_jnidir}/%{pkg_name}/%{pkg_name}.jar META-INF/p2.inf

# install *.so
install -dm 755 %{buildroot}%{_libdir}/%{pkg_name}
cp -rp target/jni/* %{buildroot}%{_libdir}/%{pkg_name}/
# create version-less symlink for .so file
pushd %{buildroot}%{_libdir}/%{pkg_name}/*
chmod +x lib%{pkg_name}-%{sover}.so
ln -s lib%{pkg_name}-%{sover}.so lib%{pkg_name}.so
popd

jar umf NATIVE-MANIFEST.MF %{buildroot}%{_jnidir}/%{pkg_name}/%{pkg_name}-native.jar
%{?scl:EOF}


%check
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
# skip tests on s390 until https://bugzilla.redhat.com/show_bug.cgi?id=1084914 is resolved
%ifnarch s390
# don't fail on unused parameters... (TODO: send patch upstream)
sed -i 's|-Werror||' libtest/GNUmakefile
ant -Duse.system.libffi=1 test
%endif
%{?scl:EOF}


%files -f .mfiles
%doc COPYING.GPL COPYING.LESSER LICENSE

%files native -f .mfiles-native
%{_libdir}/%{pkg_name}
%doc COPYING.GPL COPYING.LESSER LICENSE

%files javadoc -f .mfiles-javadoc
%doc COPYING.GPL COPYING.LESSER LICENSE

%changelog
* Fri Jul 22 2016 Mat Booth <mat.booth@redhat.com> - 1.2.10-1.2
- Avoid use of ln -r since it is not available on EL6

* Fri Jul 22 2016 Mat Booth <mat.booth@redhat.com> - 1.2.10-1.1
- Auto SCL-ise package for rh-eclipse46 collection

* Fri Feb 5 2016 Alexander Kurtakov <akurtako@redhat.com> 1.2.10-1
- Update to upstream 1.2.10 release.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.9-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jul 13 2015 Mat Booth <mat.booth@redhat.com> - 1.2.9-8
- Fix unstripped binaries and empty debuginfo package
- Ensure presence of ant-junit at buildtime
- Fixed mixed use of space and tabs

* Thu Jun 25 2015 Roland Grunberg <rgrunber@redhat.com> - 1.2.9-7
- Minor fixes to manifest as we introduce p2.inf file.

* Wed Jun 24 2015 Jeff Johnston <jjohnstn@redhat.com> 1.2.9-6
- Fix manifests so jffi requires com.kenai.jffi.native and native has bundle version.

* Tue Jun 23 2015 Roland Grunberg <rgrunber@redhat.com> - 1.2.9-5
- Add missing Bundle-SymbolicName attribute to manifest.

* Mon Jun 22 2015 Jeff Johnston <jjohnstn@redhat.com> 1.2.9-4
- Fix native MANIFEST.MF

* Thu Jun 18 2015 Jeff Johnston <jjohnstn@redhat.com> 1.2.9-3
- Add MANIFEST.MF.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 5 2015 Alexander Kurtakov <akurtako@redhat.com> 1.2.9-1
- Update to upstream 1.2.9.

* Thu Apr 30 2015 Alexander Kurtakov <akurtako@redhat.com> 1.2.8-1
- Update to upstream 1.2.8.

* Fri Feb 20 2015 Michal Srb <msrb@redhat.com> - 1.2.7-5
- Install version-less symlink for .so file

* Fri Feb 20 2015 Michal Srb <msrb@redhat.com> - 1.2.7-4
- Fix rpmlint warnings

* Fri Feb 20 2015 Michal Srb <msrb@redhat.com> - 1.2.7-3
- Install *.so file to %%{_libdir}/%%{pkg_name}/

* Tue Feb 17 2015 Michal Srb <msrb@redhat.com> - 1.2.7-2
- Build jffi-native
- Introduce javadoc subpackage

* Fri Dec 05 2014 Mo Morsi <mmorsi@redhat.com> - 1.2.7-1
- Update to JFFI 1.2.7

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 12 2014 Alexander Kurtakov <akurtako@redhat.com> 1.2.6-7
- Fix FTBFS.

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Apr 07 2014 Dan Horák <dan[at]danny.cz> - 1.2.6-5
- skip tests on s390 until https://bugzilla.redhat.com/show_bug.cgi?id=1084914 is resolved

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 1.2.6-4
- Use Requires: java-headless rebuild (#1067528)

* Sun Aug 11 2013 Mat Booth <fedora@matbooth.co.uk> - 1.2.6-3
- Remove BR on ant-nodeps, fixes FTBFS rhbz #992622

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Feb 05 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.6-1
- Updated to version 1.2.6.

* Wed Dec 19 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.0.10-4
- revbump after jnidir change

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 02 2011  Mo Morsi <mmorsi@redhat.com> - 1.0.10-1
- Updated to most recent upstream release

* Wed Jun 01 2011  Mo Morsi <mmorsi@redhat.com> - 1.0.9-1
- Updated to most recent upstream release

* Mon Oct 25 2010  <mmorsi@redhat.com> - 1.0.2-1
- Updated to most recent upstream release

* Wed Apr 14 2010  <mmorsi@redhat.com> - 0.6.5-4
- added Mamoru Tasaka's fix for ppc{,64} to prep

* Mon Mar 08 2010  <mmorsi@redhat.com> - 0.6.5-3
- fixes to jffi from feedback
- don't strip debuginfo, remove extraneous executable bits,

* Tue Feb 23 2010  <mmorsi@redhat.com> - 0.6.5-2
- fixes to jffi compilation process
- fixes to spec to conform to package guidelines

* Wed Feb 17 2010  <mmorsi@redhat.com> - 0.6.5-1
- bumped version
- fixed package to comply to fedora guidelines

* Tue Jan 19 2010  <mmorsi@redhat.com> - 0.6.2-1
- Initial build.
