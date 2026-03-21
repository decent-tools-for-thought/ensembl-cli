pkgname=ensembl-cli
pkgver=0.1.3
pkgrel=1
pkgdesc='Self-documenting command line client for the Ensembl REST API'
arch=('any')
url='https://github.com/decent-tools-for-thought/ensembl-cli'
license=('MIT')
depends=('python')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::$url/releases/download/v$pkgver/$pkgname-$pkgver.tar.gz")
sha256sums=('bb9aec95e32caa7f8bc85c722812919376542e7f53f31d50f6a0df7ee38bdb61')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  /usr/bin/python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  /usr/bin/python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
