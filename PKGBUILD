pkgname=ensembl-cli
pkgver=0.1.1
pkgrel=1
pkgdesc='Self-documenting command line client for the Ensembl REST API'
arch=('any')
url='https://github.com/decent-tools-for-thought/ensembl-cli'
license=('MIT')
depends=('python')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::$url/releases/download/v$pkgver/$pkgname-$pkgver.tar.gz")
sha256sums=('bb75c946748261da11bf2833ea617fbd6dd1d7f3f62b8505d50f2d10a5ab6753')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
