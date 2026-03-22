import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from ensembl_cli import cli


class CliTests(unittest.TestCase):
    def _run_main(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = cli.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_parser_builds_known_commands(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["api", "show", "lookup"])
        self.assertEqual(args.operation, "lookup")

    def test_top_level_help_uses_console_script_name(self) -> None:
        parser = cli.build_parser()
        self.assertTrue(parser.format_help().startswith("usage: ensembl "))

    def test_bare_invocation_prints_top_level_help(self) -> None:
        code, stdout, stderr = self._run_main([])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("usage: ensembl ", stdout)
        self.assertIn("{explain,api,raw}", stdout)

    def test_api_without_subcommand_prints_subtree_help(self) -> None:
        code, stdout, stderr = self._run_main(["api"])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("usage: ensembl api ", stdout)
        self.assertIn("{operations,show,call}", stdout)

    def test_api_call_without_operation_prints_subtree_help(self) -> None:
        code, stdout, stderr = self._run_main(["api", "call"])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("usage: ensembl api call ", stdout)
        self.assertIn("lookup", stdout)
        self.assertIn("lookup-post", stdout)

    def test_explain_surface_lists_common_workflows(self) -> None:
        code, stdout, stderr = self._run_main(["explain"])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("Common workflows:", stdout)
        self.assertIn("ensembl api operations", stdout)
        self.assertIn("ensembl raw /lookup/id/ENSG00000157764", stdout)

    def test_operations_json_output_is_machine_readable(self) -> None:
        code, stdout, stderr = self._run_main(["api", "operations", "--group", "Lookup", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertTrue(payload)
        self.assertTrue(all(item["group"] == "Lookup" for item in payload))
        self.assertIn("lookup", {item["operation_id"] for item in payload})

    def test_render_response_pretty_prints_json(self) -> None:
        rendered = cli._render_response(b'{"b":2,"a":1}', "application/json", pretty=True)
        self.assertEqual(rendered, '{\n  "b": 2,\n  "a": 1\n}')

    def test_render_response_compacts_json(self) -> None:
        rendered = cli._render_response(b'{"b":2,"a":1}', "application/json", pretty=False)
        self.assertEqual(rendered, '{"b":2,"a":1}')

    def test_render_response_leaves_plain_text_alone(self) -> None:
        rendered = cli._render_response(b"service is up", "text/plain", pretty=True)
        self.assertEqual(rendered, "service is up")


if __name__ == "__main__":
    unittest.main()
