import unittest

from ensembl_cli.cli import build_parser


class CliTests(unittest.TestCase):
    def test_parser_builds_known_commands(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["api", "show", "lookup"])
        self.assertEqual(args.operation, "lookup")


if __name__ == "__main__":
    unittest.main()
