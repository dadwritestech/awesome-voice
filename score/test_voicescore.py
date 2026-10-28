import unittest
from pathlib import Path

import voicescore as vs


class Parsing(unittest.TestCase):
    def test_frontmatter_subset(self):
        meta, body = vs.parse_frontmatter(
            "---\nname: X\nsources:\n  - https://a\n  - https://b\ntargets:\n  sentence_words: 8-18\n---\nbody")
        self.assertEqual(meta["name"], "X")
        self.assertEqual(meta["sources"], ["https://a", "https://b"])
        self.assertEqual(meta["targets"], {"sentence_words": "8-18"})
        self.assertEqual(body.strip(), "body")

    def test_every_voice_parses(self):
        voices = vs.load_voices()
        self.assertEqual(len(voices), 5)
        for v in voices:
            with self.subTest(v["slug"]):
                self.assertTrue(v["meta"].get("sources"), "needs sources")
                self.assertIn(v["meta"].get("basis"), ("published-guide", "observed"))
                self.assertGreaterEqual(len(v["banned"]), 5)
                self.assertTrue(3 <= len(v["examples"]) <= 5)
                self.assertTrue(v["targets"])


class Features(unittest.TestCase):
    def test_sentence_split_skips_headings_and_tables(self):
        text = "# Title\n\n| a | b |\n\nFirst one here. Second one here!\n\n- A list item here"
        self.assertEqual(vs.sentences(text), ["First one here.", "Second one here!", "A list item here"])

    def test_contractions(self):
        f = vs.features("You can't do that. You do not need it. It's fine.")
        self.assertEqual((f["neg_contracted"], f["neg_expanded"], f["pos_contracted"]), (1, 1, 1))

    def test_passive(self):
        self.assertEqual(vs.features("The file was deleted by the job.")["passive_rate"], 1.0)
        self.assertEqual(vs.features("The job deletes the file.")["passive_rate"], 0.0)
        self.assertEqual(vs.features("We are excited about it.")["passive_rate"], 0.0)

    def test_banned_word_boundaries(self):
        hits = vs.phrase_hits("Use the key. A keyboard is not a key-holder.", ["key"])
        self.assertEqual(hits, {"key": 1})


class SelfTest(unittest.TestCase):
    def test_after_beats_before(self):
        for v in vs.load_voices():
            for ex in v["examples"]:
                with self.subTest(voice=v["slug"], example=ex["label"]):
                    self.assertGreater(vs.score(ex["after"], v)["fit"], vs.score(ex["before"], v)["fit"])


if __name__ == "__main__":
    unittest.main()


class Check(unittest.TestCase):
    def test_replacements_parsed(self):
        v = [x for x in vs.load_voices() if x["slug"] == "gov-uk"][0]
        self.assertEqual(v["replacements"]["utilise"], "use")

    def test_check_exit_code(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write("Please utilise our seamless portal in order to submit forms!")
        try:
            self.assertEqual(vs.main(["check", "--voice", "gov-uk", "--min-fit", "90", fh.name]), 1)
            self.assertEqual(vs.main(["check", "--voice", "gov-uk", fh.name]), 0)
        finally:
            os.unlink(fh.name)
