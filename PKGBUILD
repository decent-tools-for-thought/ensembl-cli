pkgname=ensembl-cli
pkgver=0.1.2
pkgrel=1
pkgdesc='Self-documenting command line client for the Ensembl REST API'
arch=('any')
url='https://github.com/decent-tools-for-thought/ensembl-cli'
license=('MIT')
depends=('python')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::$url/releases/download/v$pkgver/$pkgname-$pkgver.tar.gz")
sha256sums=('8a26fd1fe57f92925621896c340ad86ed47a50bb2d2ff9466661d4f6c173546e')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
