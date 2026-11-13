import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import Main
from Source.Data import ProjectInfo


class EngineSelectionTests(unittest.TestCase):
    def setUp(self):
        self.Temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.Temp.cleanup)
        self.Root = Path(self.Temp.name)
        self.Project = self.Root / "Sample.uproject"
        self.Project.write_text('{"EngineAssociation": "5.2"}\n', encoding="utf-8")
        self.OriginalBytes = self.Project.read_bytes()
        self.Engines = {}
        Installations = []
        for Version in ("5.2", "5.8"):
            Engine = self.Root / f"UE {Version}"
            BatchDir = Engine / "Engine/Build/BatchFiles"
            BatchDir.mkdir(parents=True)
            (BatchDir / "Build.bat").write_text(
                '@echo off\n> "%~dp0selected.txt" echo %*\nexit /b 0\n',
                encoding="ascii",
            )
            self.Engines[Version] = Engine
            Installations.append({"AppName": f"UE_{Version}", "InstallLocation": str(Engine)})
        LauncherFile = self.Root / "Epic/UnrealEngineLauncher/LauncherInstalled.dat"
        LauncherFile.parent.mkdir(parents=True)
        LauncherFile.write_text(json.dumps({"InstallationList": Installations}), encoding="utf-8")
        self.Env = patch.dict(os.environ, {"PROGRAMDATA": str(self.Root), "LOCALAPPDATA": str(self.Root)})
        self.Env.start()
        self.addCleanup(self.Env.stop)
        self.Registry = patch.object(ProjectInfo, "GetEnginePathFromRegistry", return_value="")
        self.Registry.start()
        self.addCleanup(self.Registry.stop)

    def RunCli(self, *Args):
        Output = io.StringIO()
        PreviousDir = Path.cwd()
        try:
            os.chdir(self.Root)
            with patch("sys.argv", ["UEQuickStart", "--test", *Args]), contextlib.redirect_stdout(Output):
                Code = Main._DispatchCli()
        finally:
            os.chdir(PreviousDir)
        self.assertEqual(self.Project.read_bytes(), self.OriginalBytes)
        return Code, Output.getvalue()

    def Marker(self, Version):
        return self.Engines[Version] / "Engine/Build/BatchFiles/selected.txt"

    def test_default_build_uses_project_association(self):
        Code, _ = self.RunCli()
        self.assertEqual(Code, 0)
        self.assertTrue(self.Marker("5.2").is_file())
        self.assertFalse(self.Marker("5.8").exists())

    def test_explicit_engine_builds_with_58_without_rewriting_project(self):
        Code, Output = self.RunCli("--engine", "5.8")
        self.assertEqual(Code, 0)
        self.assertIn("Unreal Engine 5.8", Output)
        Command = self.Marker("5.8").read_text()
        self.assertIn("SampleEditor Win64 Development", Command)
        self.assertIn(f"-Project={self.Project}", Command)
        self.assertFalse(self.Marker("5.2").exists())

    def test_missing_explicit_engine_fails_without_falling_back(self):
        Code, _ = self.RunCli("--engine", "5.99")
        self.assertEqual(Code, 1)
        self.assertFalse(self.Marker("5.2").exists())
        self.assertFalse(self.Marker("5.8").exists())

    def test_selected_build_failure_is_returned(self):
        Batch = self.Engines["5.8"] / "Engine/Build/BatchFiles/Build.bat"
        Batch.write_text("@exit /b 7\n", encoding="ascii")
        Code, _ = self.RunCli("--engine", "5.8")
        self.assertEqual(Code, 1)

    def test_guid_association_keeps_existing_resolution(self):
        Guid = "{00000000-0000-0000-0000-000000000001}"
        self.Project.write_text(json.dumps({"EngineAssociation": Guid}), encoding="utf-8")
        with patch.object(ProjectInfo, "GetEnginePathFromBuilds", return_value=str(self.Engines["5.2"])):
            Info = ProjectInfo.LoadProjectInfo(self.Root)
        self.assertEqual(Info.EngineVersion, Guid)
        self.assertEqual(Info.EnginePath, str(self.Engines["5.2"]))
        self.assertFalse(Info.ErrorMsg)


if __name__ == "__main__":
    unittest.main()
