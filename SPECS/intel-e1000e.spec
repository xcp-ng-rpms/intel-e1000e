%define vendor_name Intel
%define vendor_label intel
%define driver_name e1000e

%if %undefined module_dir
%define module_dir updates
%endif

## kernel_version will be set during build because then kernel-devel
## package installs an RPM macro which sets it. This check keeps
## rpmlint happy.
%if %undefined kernel_version
%define kernel_version dummy
%endif

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}
Version: 5.10.179
Release: 2%{?dist}
License: GPL
# Sources from drivers/net/ethernet/intel/e1000e of Linux kernel v5.10.179, last
# release with patches for the e1000e driver in the 5.10.y branch
# https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/drivers/net/ethernet/intel/e1000e?h=v5.10.179
Source0: intel-e1000e-%{version}.tar.gz

# XCP-ng specific patches
Patch1000: 0001-Revert-e1000e-reject-unsupported-coalescing-params.patch
Patch1001: 0002-Revert-e1000e-extend-PTP-gettime-function-to-read-sy.patch
Patch1002: 0003-Revert-drivers-net-Call-cpu_latency_qos_-instead-of-.patch
Patch1003: 0004-Revert-e1000-e-use-new-helper-tcp_v6_gso_csum_prep.patch
Patch1004: 0005-Revert-net-move-skb-xmit_more-hint-to-softnet-data.patch
Patch1005: 0006-Revert-PM-sleep-core-Rename-DPM_FLAG_NEVER_SKIP.patch
Patch1006: 0007-Add-missing-define-for-falltrough.patch
Patch1007: 0008-Remove-txqueue-parameter-for-ndo_tx_timeout.patch
Patch1008: 0009-Add-missing-include-for-PCIE_LINK_STATE_L0S-1-define.patch
Patch1009: 0010-Show-Version.patch

BuildRequires: gcc
BuildRequires: kernel-devel
%{?_cov_buildrequires}
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n %{name}-%{version}
%{?_cov_prepare}

# Set module version to upstream kernel release
/usr/bin/echo '#define DRV_VERSION "%{version}"' >> src/e1000.h

%build
%{?_cov_wrap} %{make_build} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src KSRC=/lib/modules/%{kernel_version}/build modules

%install
%{?_cov_wrap} %{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

%{?_cov_install}

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/*/*.ko

%{?_cov_results_package}

%changelog
* Tue May 19 2025 Andrew Lindh <andrew@netplex.net> - 5.10.179-2
- Add show version for ethtool

* Tue May 06 2025 Thierry Escande <thierry.escande@vates.tech> - 5.10.179-1
- Import sources from upstream kernel v5.10.179
- Set module version to upstream kernel release

* Mon Feb 14 2022 Ross Lagerwall <ross.lagerwall@citrix.com> - 3.8.7-2
- CP-38416: Enable static analysis

* Mon Jan 24 2022 Deli Zhang <deli.zhang@citrix.com> - 3.8.7-1
- CP-38362: Update intel-e1000e driver to 3.8.7

* Wed Dec 02 2020 Ross Lagerwall <ross.lagerwall@citrix.com> - 3.4.2.1-2
- CP-35517: Fix build for koji
