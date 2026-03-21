pkgname=ensembl-cli
pkgver=0.1.0
pkgrel=1
pkgdesc='Self-documenting command line client for the Ensembl REST API'
arch=('any')
url='https://github.com/decent-tools-for-thought/ensembl-cli'
license=('MIT')
depends=('python')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::$url/releases/download/v$pkgver/$pkgname-$pkgver.tar.gz")
sha256sums=('cea1e1ab94af33ac41776c4f9755ff995ffe5a99e27c8c02ec6660096337923c')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
