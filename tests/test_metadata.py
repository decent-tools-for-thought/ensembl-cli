import unittest

from ensembl_cli.metadata import get_operation, load_metadata, load_operations


class MetadataTests(unittest.TestCase):
    def test_metadata_snapshot_is_present(self) -> None:
        metadata = load_metadata()
        self.assertGreater(metadata["operation_count"], 0)
        self.assertTrue(metadata["docs_version"])

    def test_operation_ids_are_unique(self) -> None:
        operations = load_operations()
        ids = [item.operation_id for item in operations]
        self.assertEqual(len(ids), len(set(ids)))

    def test_metadata_operation_count_matches_loaded_operations(self) -> None:
        metadata = load_metadata()
        self.assertEqual(metadata["operation_count"], len(load_operations()))

    def test_path_params_are_declared(self) -> None:
        for operation in load_operations():
            declared = {item.name for item in operation.params if item.location == "path"}
            self.assertTrue(set(operation.path_params).issubset(declared))

    def test_get_operation_accepts_aliases(self) -> None:
        canonical = get_operation("lookup_post")
        alias = get_operation("lookup-post")
        self.assertEqual(alias.operation_id, canonical.operation_id)
        self.assertEqual(alias.method, "POST")


if __name__ == "__main__":
    unittest.main()
