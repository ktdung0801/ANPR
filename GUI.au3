
#NoTrayIcon

#region ---Head--
#include <Constants.au3>
#include <GUIConstantsEx.au3>
#include <Misc.au3>
#include <WindowsConstants.au3>
#include <Array.au3>
#include <File.au3>
#include <MsgBoxConstants.au3>
#include <FileConstants.au3>
#include <ButtonConstants.au3>
#include <StaticConstants.au3>
#include <FontConstants.au3>
Global $hGUI,$Button_1,$Button_2,$Button_3,$Label_3
FileInstall("gui_img.jpg", @TempDir & "\gui_img.jpg", 1)
create_form()
#endregion ---Head---

#region --- Form ---

func create_form()
DirCreate(@ScriptDir & "\visualize")
DirCreate(@ScriptDir & "\output")
$hGUI=GuiCreate("License Plate Recognition", 650, 367, -1, -1, $WS_OVERLAPPED + $WS_CAPTION + $WS_SYSMENU + $WS_VISIBLE + $WS_CLIPSIBLINGS + $WS_MINIMIZEBOX)
$Pic_2 = GuiCtrlCreatePic(@TempDir & "\gui_img.jpg", 0, 0, 650, 367, -1)

GUICtrlSetBkColor(-1,$GUI_BKCOLOR_TRANSPARENT)
GUICtrlSetState(-1, $GUI_DISABLE)
$Button_1 = GuiCtrlCreateButton("Folder Ảnh", 100, 270, 100, 40,-1)
GUICtrlSetBkColor(-1, $COLOR_WHITE)
$Button_2 = GuiCtrlCreateButton("Một Ảnh", 450, 270, 100, 40,-1)
GUICtrlSetBkColor(-1, $COLOR_WHITE)
$Button_3 = GuiCtrlCreateButton("Video", 280, 270, 100, 40,-1)
GUICtrlSetBkColor(-1, $COLOR_WHITE)
$Label_3 = GuiCtrlCreateLabel("", 275, 320, 100, 20,bitor($SS_CENTER,$SS_CENTERIMAGE,0,0))
GUICtrlSetBkColor(-1, $COLOR_WHITE)
GUICtrlSetFont($Label_3, 12, $FW_DONTCARE , $GUI_FONTNORMAL, "Times New Roman",$CLEARTYPE_QUALITY)
GUICtrlSetFont($Button_1, 15, $FW_DONTCARE, $GUI_FONTNORMAL, "Times New Roman",$CLEARTYPE_QUALITY)
GUICtrlSetFont($Button_2, 15, $FW_DONTCARE, $GUI_FONTNORMAL, "Times New Roman",BitOR($CLEARTYPE_QUALITY, $ANTIALIASED_QUALITY))
GUICtrlSetFont($Button_3, 15, $FW_DONTCARE, $GUI_FONTNORMAL, "Times New Roman",BitOR($CLEARTYPE_QUALITY, $ANTIALIASED_QUALITY))
GuiSetState()
endfunc
#EndRegion --- Form ---

#region --- Loop ---
While 1
	$msg = GuiGetMsg()
	Select
	Case $msg = $GUI_EVENT_CLOSE
		ExitLoop
	Case $msg = $Button_1
		FolderImg()
	Case $msg = $Button_2
		OneImg()
	Case $msg = $Button_3
		LoadVideo()
	Case Else
		;;;
	EndSelect
WEnd
#Endregion --- Loop ---

#Region --- Additional Functions ---
Func FolderImg()

	$PathFolder = FileSelectFolder("Select folder", @ScriptDir)
	if @error then Return

	$cmd = "python main.py -f " & '"' & $PathFolder & '"'  & "&pause"

	RunWait(@ComSpec & " /c " & $cmd, @ScriptDir, @SW_SHOW)
	$cmd = "explorer.exe " & '"' & @ScriptDir & "\output" & '"'
	Run($cmd)
EndFunc


Func OneImg()
	$PathImg = FileOpenDialog("Select image", @ScriptDir, "Image (*.*)", $FD_FILEMUSTEXIST)
	if @error then Return
	$cmd = "python main.py -i " & '"' & $PathImg & '"'  & "&pause"
	RunWait(@ComSpec & " /c " & $cmd, @ScriptDir, @SW_SHOW)
	$cmd = "explorer.exe " & '"' & @ScriptDir & "\visualize" & '"'
	Run($cmd)
Endfunc
#Endregion --- Additional Functions ---
Exit

Func LoadVideo()
	$PathVideo = FileOpenDialog("Select video", @ScriptDir, "Video (*.*)", $FD_FILEMUSTEXIST)
	if @error then Return
	$cmd = "python main.py -v " & '"' & $PathVideo & '"'
	RunWait(@ComSpec & " /c " & $cmd, @ScriptDir, @SW_SHOW)
Endfunc
