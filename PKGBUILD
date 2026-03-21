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
sha256sums=('4e6728f1fdbf06cceee72d045371586355424bc0c180e57292db13775df17414')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
