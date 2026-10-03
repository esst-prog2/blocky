# Creates a "Blocky" shortcut in the Start menu with Blocky's icon.
# Right-click it in Start and choose "Pin to taskbar" (Windows does not let programs pin themselves).
# The shortcut carries the app ID "Blocky", the same one Blocky sets while running,
# so the pinned icon and the open window share one taskbar button.
#
# Run from anywhere: powershell -ExecutionPolicy Bypass -File tools\create_shortcut.ps1

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
# Prefer the project's virtual environment, so Blocky runs with the packages from requirements.txt.
$venvPythonw = Join-Path $repo ".venv\Scripts\pythonw.exe"
$pythonw = if (Test-Path $venvPythonw) { $venvPythonw } else { (Get-Command pythonw -ErrorAction Stop).Source }
$icon = Join-Path $repo "blocky\assets\blocky.ico"
$shortcut = Join-Path ([Environment]::GetFolderPath("Programs")) "Blocky.lnk"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
using System.Text;

public static class BlockyShortcut
{
    [ComImport, Guid("00021401-0000-0000-C000-000000000046")]
    class ShellLink {}

    [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("000214F9-0000-0000-C000-000000000046")]
    interface IShellLinkW
    {
        void GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder file, int size, IntPtr data, uint flags);
        void GetIDList(out IntPtr list);
        void SetIDList(IntPtr list);
        void GetDescription([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder text, int size);
        void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string text);
        void GetWorkingDirectory([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder dir, int size);
        void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string dir);
        void GetArguments([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder args, int size);
        void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string args);
        void GetHotkey(out short key);
        void SetHotkey(short key);
        void GetShowCmd(out int cmd);
        void SetShowCmd(int cmd);
        void GetIconLocation([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder path, int size, out int index);
        void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string path, int index);
        void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string path, uint reserved);
        void Resolve(IntPtr window, uint flags);
        void SetPath([MarshalAs(UnmanagedType.LPWStr)] string path);
    }

    [StructLayout(LayoutKind.Sequential, Pack = 4)]
    struct PropertyKey { public Guid Format; public uint Id; }

    [StructLayout(LayoutKind.Sequential)]
    class PropVariant { public ushort Type; ushort r1, r2, r3; public IntPtr Value; public IntPtr Extra; }

    [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
    interface IPropertyStore
    {
        void GetCount(out uint count);
        void GetAt(uint index, out PropertyKey key);
        void GetValue(ref PropertyKey key, [Out] PropVariant value);
        void SetValue(ref PropertyKey key, [In] PropVariant value);
        void Commit();
    }

    public static void Create(string path, string target, string args, string workDir, string icon, string appId)
    {
        var link = (IShellLinkW)new ShellLink();
        link.SetPath(target);
        link.SetArguments(args);
        link.SetWorkingDirectory(workDir);
        link.SetIconLocation(icon, 0);
        link.SetDescription("Blocky: fewer distractions, on your schedule");

        var key = new PropertyKey { Format = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"), Id = 5 };
        var value = new PropVariant { Type = 31, Value = Marshal.StringToCoTaskMemUni(appId) };  // VT_LPWSTR
        var store = (IPropertyStore)link;
        store.SetValue(ref key, value);
        store.Commit();
        Marshal.FreeCoTaskMem(value.Value);

        ((IPersistFile)link).Save(path, true);
    }
}
"@

[BlockyShortcut]::Create($shortcut, $pythonw, "-m blocky", $repo, $icon, "Blocky")
Write-Host "Created $shortcut"
Write-Host "Open Start, find Blocky, right-click it and choose 'Pin to taskbar'."
