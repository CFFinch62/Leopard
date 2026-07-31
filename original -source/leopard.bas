' Leopard - Created by Brandon Watts
' E-mail: brandonwatts@adelphia.net
' Web: http://www.leopardprogramming.com
' This software is licensed under the CC-GNU GPL.
' DO NOT EDIT OR REMOVE THE TEXT ABOVE!


WindowWidth = 500
WindowHeight = 355

nomainwin

open "color.dat" for input as #forecolor
Line Input #forecolor, forecolor$
close #forecolor
ForegroundColor$ = ""; forecolor$

exe$ = "closed"
nex = 0
save = 0
textbpcheck$ = "stop"
textbptwocheck$ = "stop"
textbpthreecheck$ = "stop"
textbpfourcheck$ = "stop"
textbpfivecheck$ = "stop"
textepcheck$ = "stop"
texteptwocheck$ = "stop"
textepthreecheck$ = "stop"
textepfourcheck$ = "stop"
textepfivecheck$ = "stop"
fontcheck$ = "stop"
colorcheck$ = "stop"
backcheck$ = "stop"
textcontinue$ = "stop"
tppcontinue$ = "stop"
tpcconfirm$ = "stop"
spritebcheck$ = "stop"
openmp3continue$ = "stop"
maxcontinue$ = "stop"
mincontinue$ = "stop"

texteditor #main.text, 6, 36, 481, 263
bmpbutton #main.bmpbutton1, "New.bmp", [BmpButton1], UL, 6, 11
bmpbutton #main.bmpbutton3, "Open.bmp", [OpenFile], UL, 37, 11
bmpbutton #main.bmpbutton2, "Run.bmp", [BmpButton2], UL, 110, 12
bmpbutton #main.bmpbutton4, "Save.bmp", [SaveFile], UL, 70, 12
bmpbutton #main.bmpbutton5, "Compile.bmp", [CompileFile], UL, 141, 12
bmpbutton #main.bmpbutton6, "Help.bmp", [HelpTopics], UL, 181, 11
menu #main, "&File", "&New...", [BmpButton1], |, "&Open...", [OpenFile], "&Save...", [SaveFile], |, "&Exit", [Quit]
menu #main, "Edit"
menu #main, "&Run", "&Execute", [BmpButton2], |, "&Compile", [CompileFile]
menu #main, "&Options", "&Change Font", [ChangeFont], "Change &Text Color", [Loop], |, "&Print Code", [PrintCode]
menu #main, "Change Text Color", "Black", [BlackText], "Blue", [BlueText], "Brown", [BrownText], "Buttonface", [ButtonfaceText], "Cyan", [CyanText],_
"Dark Blue", [DarkBlueText], "Dark Cyan", [DarkCyanText], "Dark Gray", [DarkGrayText], "Dark Green", [DarkGreenText],_
"Dark Pink", [DarkPinkText], "Dark Red", [DarkRedText], "Green", [GreenText], "Light Gray", [LightGrayText],_
"Pale Gray", [PaleGrayText], "Pink", [PinkText], "Red", [RedText], "Yellow", [YellowText]
menu #main, "&Help", "&Help Topics", [HelpTopics], |, "&About", [AboutLeopard]
open "Leopard" for window as #main
open "user32.dll" for dll as #user
open "winmm.dll" for dll as #mm
print #main, "trapclose [Quit]"

open "font.dat" for input as #fontchange
Line Input #fontchange, specifiedfont$
close #fontchange
print #main, "font "; specifiedfont$

print #main.text, "!autoresize"

z = hwnd(#main)

CallDll #user, "GetMenu",_
z as long,_
hMenu1 as long

CallDll #user, "GetSubMenu",_
hMenu1 As long,_
3 As long, _
hmenuFile As long

CallDll #user, "GetSubMenu",_
hMenu1 As long,_
4 As long,_
hmenuRecent As long

flags = _MF_BYPOSITION Or _MF_POPUP Or _MF_STRING

CallDll #user, "ModifyMenuA",_
hmenuFile As long, _
1 As long,_
flags As long, _
hmenuRecent As long,_
"Change &Text Color" As ptr, _
result As long

CallDll #user, "RemoveMenu",_
hMenu1 As long, _
4 As long,_
_MF_BYPOSITION As long, _
result As long

CallDll #user, "DrawMenuBar", z As long, result As void

[Loop]
wait

[BmpButton1]
print #main.text, "!cls"
NewText2$ = "Leopard"
calldll #user, "SetWindowTextA",_
z as word,_
NewText2$ as ptr,_
result as void
goto [Loop]


[BmpButton2]
'print #main.text, "!selectall";
print #main.text, "!copy" ;
print #main.text, "!contents?"
input #main.text, code$
if code$ = "" then goto [Error]
open "Code.txt" for output as #code
print #code, ""; code$
if instr(code$,"end")>0 then goto [Continue]
goto [EndProblem]

[Continue]
close #code

open "Code.txt" for input as #code
code$=lower$(code$)
goto [Begin]

[Begin]
Line Input #code, wtype$

if wtype$ = "window" then goto [Window]
if wtype$ = "text window" then goto [TextWindow]
if wtype$ = "graphics window" then goto [GraphicsWindow]
if wtype$ = "no window" then goto [InvisWindow]
goto [Begin]

[Quit]
confirm "Really Quit?"; reallyquitanswer$
if reallyquitanswer$ = "no" then goto [Loop]
close #main
close #user
close #mm
end

[Window]
Line Input #code, pretitle$
if pretitle$ = "window title" then gosub [Title]
if nex = 1 then goto [PreW]
goto [Window]

[TextWindow]
Line Input #code, pretitle$
if pretitle$ = "window title" then gosub [Title]
if nex = 1 then goto [PreW2]
goto [TextWindow]

[GraphicsWindow]
Line Input #code, pretitle$
if pretitle$ = "window title" then gosub [Title]
if nex = 1 then goto [PreW3]
goto [GraphicsWindow]

[PreW]
nex = 0
Line Input #code, prew$
if prew$ = "window size" then gosub [Size]
if nex = 1 then goto [Start]
goto [PreW]

[PreW2]
nex = 0
Line Input #code, prew$
if prew$ = "window size" then gosub [Size]
if nex = 1 then goto [TextStart]
goto [PreW2]

[PreW3]
nex = 0
Line Input #code, prew$
if prew$ = "window size" then gosub [Size]
if nex = 1 then goto [GraphicsStart]
goto [PreW3]

[TextStart]
WindowWidth = w
WindowHeight = h

nomainwin

goto [TextCheck]

[TextCheck]
Line Input #code, textcheck$
if textcheck$ = "print text" then gosub [PrintTextW]
if textcheck$ = "open file" then gosub [TextOpenFile]
if textcheck$ = "end" then goto [Execute2]
goto [TextCheck]

[GraphicsStart]
if exe$ = "running" then close #win
exe$ = "running"

WindowWidth = w
WindowHeight = h

nomainwin

open ""; title$ for graphics_nsb as #win
print #win, "trapclose [Close]"

goto [GraphicsBL]

[GraphicsBL]
Line Input #code, textbp$
if textbp$ = "up" then gosub [Up]
if textbp$ = "down" then gosub [Down]
if textbp$ = "home" then gosub [Home]
if textbp$ = "go" then gosub [GraphicsGo]
if textbp$ = "goto" then gosub [GraphicsGoTo]
if textbp$ = "place" then gosub [Place]
if textbp$ = "turn" then gosub [Turn]
if textbp$ = "north" then gosub [North]
if textbp$ = "fill" then gosub [Fill]
if textbp$ = "pen" then gosub [Pen]
if textbp$ = "size" then gosub [PenSize]
if textbp$ = "font" then gosub [PenFont]
if textbp$ = "text" then gosub [PenText]
if textbp$ = "backcolor" then gosub [BackColor]
if textbp$ = "box" then gosub [Box]
if textbp$ = "boxfilled" then gosub [BoxFilled]
if textbp$ = "circle" then gosub [Circle]
if textbp$ = "circlefilled" then gosub [CircleFilled]
if textbp$ = "drawbmp" then gosub [DrawBMPG]
if textbp$ = "ellipse" then gosub [Ellipse]
if textbp$ = "ellipsefilled" then gosub [EllipseFilled]
if textbp$ = "end" then gosub [EndGraphics]
goto [GraphicsBL]

[Up]
print #win, "up"
return

[Down]
print #win, "down"
return

[Home]
print #win, "home"
return

[GraphicsGo]
Line Input #code, gographic$
print #win, "go "; gographic$
return

[GraphicsGoTo]
Line Input #code, gotographic$
print #win, "goto "; gotographic$
return

[Place]
Line Input #code, placeit$
print #win, "place "; placeit$
return

[Turn]
Line Input #code, turnit$
print #win, "turn "; turnit$
return

[North]
print #win, "north"
return

[Fill]
Line Input #code, fillcolor$
print #win, "fill "; fillcolor$
return

[Pen]
Line Input #code, pencolor$
print #win, "color "; pencolor$
return

[PenSize]
Line Input #code, pensize$
print #win, "size "; pensize$
return

[PenText]
Line Input #code, pentext$
print #win, "\ "; pentext$
return

[Box]
Line Input #code, boxx$
Line Input #code, boxy$
print #win, "box ";boxx;" ";boxy
return

[BackColor]
Line Input #code, gbackcolor$
print #win, "backcolor "; gbackcolor$
return

[Circle]
Line Input #code, circler$
print #win, "circle "; circler$
return

[CircleFilled]
Line Input #code, circlefillr$
print #win, "circlefilled "; circlefillr$
return

[BoxFilled]
Line Input #code, boxfillx$
Line Input #code, boxfilly$
print #win, "boxfilled ";boxfillx;" ";boxfilly
return

[DrawBMPG]
Line Input #code, bmpgname$
Line Input #code, bmpx
Line Input #code, bmpy
loadbmp "bmpg", ""; bmpgname$
print #win, "drawbmp bmpg ";bmpx;" ";bmpy
return

[Ellipse]
Line Input #code, ellipsex
Line Input #code, ellipsey
print #win, "ellipse ";ellipsex;" ";ellipsey
return

[EllipseFilled]
Line Input #code, ellipsefx
Line Input #code, ellipsefy
print #win, "ellipsefilled ";ellipsefx;" ";ellipsefy
return

[PenFont]
Line Input #code, penfont$
print #win, "font "; penfont$
return

[EndGraphics]
print #win, "flush"
close #code
goto [Loop]

[Execute2]
if exe$ = "running" then close #win
exe$ = "running"
close #code

open ""; title$ for text as #win
print #win, "!trapclose [Close]"

if textcontinue$ = "continue" then print #win, ""; textfortext$
if textstartgo$ = "go" then gosub [Proceed]

textcontinue$ = "stop"
textstartgo$ = "stop"

[Loop3]
wait

[Start]
WindowWidth = w
WindowHeight = h

nomainwin

goto [TextBL]

[TextBL]
Line Input #code, textbp$
if textbp$ = "varone" then gosub [Var1]
if textbp$ = "vartwo" then gosub [Var2]
if textbp$ = "varthree" then gosub [Var3]
if textbp$ = "varfour" then gosub [Var4]
if textbp$ = "varfive" then gosub [Var5]
if textbp$ = "textbox" then gosub [TextB]
if textbp$ = "textboxtwo" then gosub [TextB2]
if textbp$ = "textboxthree" then gosub [TextB3]
if textbp$ = "textboxfour" then gosub [TextB4]
if textbp$ = "textboxfive" then gosub [TextB5]
if textbp$ = "textedit" then gosub [TextE]
if textbp$ = "textedittwo" then gosub [TextE2]
if textbp$ = "texteditthree" then gosub [TextE3]
if textbp$ = "texteditfour" then gosub [TextE4]
if textbp$ = "texteditfive" then gosub [TextE5]
if textbp$ = "print textbox" then gosub [TextBP]
if textbp$ = "print textboxtwo" then gosub [TextBP2]
if textbp$ = "print textboxthree" then gosub [TextBP3]
if textbp$ = "print textboxfour" then gosub [TextBP4]
if textbp$ = "print textboxfive" then gosub [TextBP5]
if textbp$ = "print textedit" then gosub [TextEP]
if textbp$ = "print textedittwo" then gosub [TextEP2]
if textbp$ = "print texteditthree" then gosub [TextEP3]
if textbp$ = "print texteditfour" then gosub [TextEP4]
if textbp$ = "print texteditfive" then gosub [TextEP5]
if textbp$ = "font" then gosub [SpecifyFont]
if textbp$ = "text color" then gosub [SpecifyColor]
if textbp$ = "background color" then gosub [BackgroundColor]
if textbp$ = "textbox color" then gosub [TextboxColor]
if textbp$ = "textedit color" then gosub [TexteditColor]
if textbp$ = "combobox color" then gosub [ComboboxColor]
if textbp$ = "listbox color" then gosub [ListboxColor]
if textbp$ = "text" then gosub [PrintText]
if textbp$ = "texttwo" then gosub [PrintText2]
if textbp$ = "textthree" then gosub [PrintText3]
if textbp$ = "textfour" then gosub [PrintText4]
if textbp$ = "textfive" then gosub [PrintText5]
if textbp$ = "button" then gosub [WinButton]
if textbp$ = "buttontwo" then gosub [WinButton2]
if textbp$ = "buttonthree" then gosub [WinButton3]
if textbp$ = "buttonfour" then gosub [WinButton4]
if textbp$ = "buttonfive" then gosub [WinButton5]
if textbp$ = "bmpbutton" then gosub [WinBmpButton]
if textbp$ = "bmpbuttontwo" then gosub [WinBmpButton2]
if textbp$ = "bmpbuttonthree" then gosub [WinBmpButton3]
if textbp$ = "bmpbuttonfour" then gosub [WinBmpButton4]
if textbp$ = "bmpbuttonfive" then gosub [WinBmpButton5]
if textbp$ = "listbox" then gosub [WinListBox]
if textbp$ = "combobox" then gosub [WinComboBox]
if textbp$ = "radiobutton" then gosub [WinRadioButton]
if textbp$ = "radiobuttontwo" then gosub [WinRadioButton2]
if textbp$ = "radiobuttonthree" then gosub [WinRadioButton3]
if textbp$ = "radiobuttonfour" then gosub [WinRadioButton4]
if textbp$ = "radiobuttonfive" then gosub [WinRadioButton5]
if textbp$ = "checkbox" then gosub [WinCheckBox]
if textbp$ = "checkboxtwo" then gosub [WinCheckBox2]
if textbp$ = "checkboxthree" then gosub [WinCheckBox3]
if textbp$ = "checkboxfour" then gosub [WinCheckBox4]
if textbp$ = "checkboxfive" then gosub [WinCheckBox5]
if textbp$ = "groupbox" then gosub [WinGroupBox]
if textbp$ = "groupboxtwo" then gosub [WinGroupBox2]
if textbp$ = "groupboxthree" then gosub [WinGroupBox3]
if textbp$ = "groupboxfour" then gosub [WinGroupBox4]
if textbp$ = "groupboxfive" then gosub [WinGroupBox5]
if textbp$ = "menu" then gosub [WinMenu]
if textbp$ = "print listbox" then gosub [WinLP]
if textbp$ = "print listboxtwo" then gosub [WinLP2]
if textbp$ = "print listboxthree" then gosub [WinLP3]
if textbp$ = "print listboxfour" then gosub [WinLP4]
if textbp$ = "print listboxfive" then gosub [WinLP5]
if textbp$ = "listbox onclick" then gosub [LCOC]
if textbp$ = "listboxtwo onclick" then gosub [LCOC2]
if textbp$ = "listboxthree onclick" then gosub [LCOC3]
if textbp$ = "listboxfour onclick" then gosub [LCOC4]
if textbp$ = "listboxfive onclick" then gosub [LCOC5]
if textbp$ = "print combobox" then gosub [WinCP]
if textbp$ = "print comboboxtwo" then gosub [WinCP2]
if textbp$ = "print comboboxthree" then gosub [WinCP3]
if textbp$ = "print comboboxfour" then gosub [WinCP4]
if textbp$ = "print comboboxfive" then gosub [WinCP5]
if textbp$ = "combobox onclick" then gosub [CCOC]
if textbp$ = "comboboxtwo onclick" then gosub [CCOC2]
if textbp$ = "comboboxthree onclick" then gosub [CCOC3]
if textbp$ = "comboboxfour onclick" then gosub [CCOC4]
if textbp$ = "comboboxfive onclick" then gosub [CCOC5]
if textbp$ = "button onclick" then gosub [BOC]
if textbp$ = "buttontwo onclick" then gosub [BOC2]
if textbp$ = "buttonthree onclick" then gosub [BOC3]
if textbp$ = "buttonfour onclick" then gosub [BOC4]
if textbp$ = "buttonfive onclick" then gosub [BOC5]
if textbp$ = "bmpbutton onclick" then gosub [BBOC]
if textbp$ = "bmpbuttontwo onclick" then gosub [BBOC2]
if textbp$ = "bmpbuttonthree onclick" then gosub [BBOC3]
if textbp$ = "bmpbuttonfour onclick" then gosub [BBOC4]
if textbp$ = "bmpbuttonfive onclick" then gosub [BBOC5]
if textbp$ = "radiobutton onclick" then gosub [RBOC]
if textbp$ = "radiobuttontwo onclick" then gosub [RBOC2]
if textbp$ = "radiobuttonthree onclick" then gosub [RBOC3]
if textbp$ = "radiobuttonfour onclick" then gosub [RBOC4]
if textbp$ = "radiobuttonfive onclick" then gosub [RBOC5]
if textbp$ = "checkbox onclick" then gosub [CBOC]
if textbp$ = "checkboxtwo onclick" then gosub [CBOC2]
if textbp$ = "checkboxthree onclick" then gosub [CBOC3]
if textbp$ = "checkboxfour onclick" then gosub [CBOC4]
if textbp$ = "checkboxfive onclick" then gosub [CBOC5]
if textbp$ = "menu onclick" then gosub [MBOC]
if textbp$ = "playwav" then gosub [TPP]
if textbp$ = "play mp3" then gosub [OpenPMP3]
if textbp$ = "maximize" then gosub [PreMax]
if textbp$ = "minimize" then gosub [PreMin]
if textbp$ = "confirm" then gosub [TPC]
if textbp$ = "end" then gosub [Execute]
goto [TextBL]

[Execute]
if exe$ = "running" then close #win
exe$ = "running"
close #code

if colorcheck$ = "stop" then gosub [GetColor]
ForegroundColor$ = ""; colorone$

if backcheck$ = "stop" then gosub [GetBackgroundColor]
BackgroundColor$ = ""; backcolor$

open ""; title$ for window as #win
print #win, "trapclose [Close]"

if fontcheck$ = "continue" then print #win, "font "; fontone$
if textbpcheck$ = "continue" then print #win.textbox, ""; textbpone$
if textbptwocheck$ = "continue" then print #win.textbox2, ""; textbptwo$
if textbpthreecheck$ = "continue" then print #win.textbox3, ""; textbpthree$
if textbpfourcheck$ = "continue" then print #win.textbox4, ""; textbpfour$
if textbpfivecheck$ = "continue" then print #win.textbox5, ""; textbpfive$
if textepcheck$ = "continue" then print #win.textedit, ""; textepone$
if texteptwocheck$ = "continue" then print #win.textedit2, ""; texteptwo$
if textepthreecheck$ = "continue" then print #win.textedit3, ""; textepthree$
if textepfourcheck$ = "continue" then print #win.textedit4, ""; textepfour$
if textepfivecheck$ = "continue" then print #win.textedit5, ""; textepfive$
if tppcontinue$ = "continue" then playwave ""; tppevent$, async
if openmp3continue$ = "continue" then gosub [PlayIt]
if spritebcheck$ = "continue" then gosub [SpriteBC]
if maxcontinue$ = "continue" then gosub [BOCMAX]
if mincontinue$ = "continue" then gosub [BOCMIN]

fontcheck$ = "stop"
textbpcheck$ = "stop"
textbptwocheck$ = "stop"
textbpthreecheck$ = "stop"
textbpfourcheck$ = "stop"
textbpfivecheck$ = "stop"
textepcheck$ = "stop"
texteptwocheck$ = "stop"
textepthreecheck$ = "stop"
textepfourcheck$ = "stop"
textepfivecheck$ = "stop"
colorcheck$ = "stop"
backcheck$ = "stop"
tppcontinue$ = "stop"
spritebcheck$ = "stop"
openmp3continue$ = "stop"
maxcontinue$ = "stop"
mincontinue$ = "stop"
array$(0) = ""
array$(1) = ""
array$(2) = ""
array$(3) = ""
array$(4) = ""
array2$(0) = ""
array2$(1) = ""
array2$(2) = ""
array2$(3) = ""
array2$(4) = ""

[Loop2]
wait

[Close]
if tpcconfirm$ = "continue" then confirm tpcevent$; answer$
if answer$ = "no" then goto [Loop2]
tpcconfirm$ = "stop"
exe$ = "closed"
nex = 0
boce$ = ""
boct$ = ""
bocw$ = ""
cboce$ = ""
cboct$ = ""
cbocw$ = ""
bboce$ = ""
bboct$ = ""
bbocw$ = ""
rboce$ = ""
rboct$ = ""
rbocw$ = ""
mboce$ = ""
mboct$ = ""
mbocw$ = ""
playwave ""
cursor normal
r$=mciSendStringA$("close music")
r$=mciSendString$("close movie")
varone$ = ""
vartwo$ = ""
varthree$ = ""
varfour$ = ""
varfive$ = ""
textbcolor$ = ""
TextboxColor$ = ""
textecolor$ = ""
TexteditorColor$ = ""
combobcolor$ = ""
ComboboxColor$ = ""
listbcolor$ = ""
ListboxColor$ = ""
close #win
goto [Loop]

[Title]
Line Input #code, title$
nex = 1
return

[Size]
Line Input #code, w
Line Input #code, h
nex = 1
return

[TextB]
Line Input #code, textone
Line Input #code, texttwo
Line Input #code, textthree
Line Input #code, textfour
textbox #win.textbox, textone, texttwo, textthree, textfour
return

[TextB2]
Line Input #code, textonetwo
Line Input #code, texttwotwo
Line Input #code, textthreetwo
Line Input #code, textfourtwo
textbox #win.textbox2, textonetwo, texttwotwo, textthreetwo, textfourtwo
return

[TextB3]
Line Input #code, textonethree
Line Input #code, texttwothree
Line Input #code, textthreethree
Line Input #code, textfourthree
textbox #win.textbox3, textonethree, texttwothree, textthreethree, textfourthree
return

[TextB4]
Line Input #code, textonefour
Line Input #code, texttwofour
Line Input #code, textthreefour
Line Input #code, textfourfour
textbox #win.textbox4, textonefour, texttwofour, textthreefour, textfourfour
return

[TextB5]
Line Input #code, textonefive
Line Input #code, texttwofive
Line Input #code, textthreefive
Line Input #code, textfourfive
textbox #win.textbox5, textonefive, texttwofive, textthreefive, textfourfive
return

[TextE]
Line Input #code, texteone
Line Input #code, textetwo
Line Input #code, textethree
Line Input #code, textefour
texteditor #win.textedit, texteone, textetwo, textethree, textefour
return

[TextE2]
Line Input #code, texteonetwo
Line Input #code, textetwotwo
Line Input #code, textethreetwo
Line Input #code, textefourtwo
texteditor #win.textedit2, texteonetwo, textetwotwo, textethreetwo, textefourtwo
return

[TextE3]
Line Input #code, texteonethree
Line Input #code, textetwothree
Line Input #code, textethreethree
Line Input #code, textefourthree
texteditor #win.textedit3, texteonethree, textetwothree, textethreethree, textefourthree
return

[TextE4]
Line Input #code, texteonefour
Line Input #code, textetwofour
Line Input #code, textethreefour
Line Input #code, textefourfour
texteditor #win.textedit4, texteonefour, textetwofour, textethreefour, textefourfour
return

[TextE5]
Line Input #code, texteonefive
Line Input #code, textetwofive
Line Input #code, textethreefive
Line Input #code, textefourfive
texteditor #win.textedit5, texteonefive, textetwofive, textethreefive, textefourfive
return

[TextBP]
Line Input #code, textbpone$
textbpcheck$ = "continue"
return

[TextBP2]
Line Input #code, textbptwo$
textbptwocheck$ = "continue"
return

[TextBP3]
Line Input #code, textbpthree$
textbpthreecheck$ = "continue"
return

[TextBP4]
Line Input #code, textbpfour$
textbpfourcheck$ = "continue"
return

[TextBP5]
Line Input #code, textbpfive$
textbpfivecheck$ = "continue"
return

[TextEP]
Line Input #code, textepone$
textepcheck$ = "continue"
return

[TextEP2]
Line Input #code, texteptwo$
texteptwocheck$ = "continue"
return

[TextEP3]
Line Input #code, textepthree$
textepthreecheck$ = "continue"
return

[TextEP4]
Line Input #code, textepfour$
textepfourcheck$ = "continue"
return

[TextEP5]
Line Input #code, textepfive$
textepfivecheck$ = "continue"
return

[SpecifyFont]
Line Input #code, fontone$
fontcheck$ = "continue"
return

[SpecifyColor]
Line Input #code, colorone$
colorcheck$ = "continue"
return

[GetColor]
colorone$ = "black"
return

[PrintText]
Line Input #code, stext$
Line Input #code, stextone
Line Input #code, stexttwo
Line Input #code, stextthree
Line Input #code, stextfour
statictext #win.statictext, ""; stext$, stextone, stexttwo, stextthree, stextfour
return

[PrintText2]
Line Input #code, stexttwo$
Line Input #code, stextonetwo
Line Input #code, stexttwotwo
Line Input #code, stextthreetwo
Line Input #code, stextfourtwo
statictext #win.statictext2, ""; stexttwo$, stextonetwo, stexttwotwo, stextthreetwo, stextfourtwo
return

[PrintText3]
Line Input #code, stextthree$
Line Input #code, stextonethree
Line Input #code, stexttwothree
Line Input #code, stextthreethree
Line Input #code, stextfourthree
statictext #win.statictext3, ""; stextthree$, stextonethree, stexttwothree, stextthreethree, stextfourthree
return

[PrintText4]
Line Input #code, stextfour$
Line Input #code, stextonefour
Line Input #code, stexttwofour
Line Input #code, stextthreefour
Line Input #code, stextfourfour
statictext #win.statictext4, ""; stextfour$, stextonefour, stexttwofour, stextthreefour, stextfourfour
return

[PrintText5]
Line Input #code, stextfive$
Line Input #code, stextonefive
Line Input #code, stexttwofive
Line Input #code, stextthreefive
Line Input #code, stextfourfive
statictext #win.statictext5, ""; stextfive$, stextonefive, stexttwofive, stextthreefive, stextfourfive
return

[WinButton]
Line Input #code, winbtext$
Line Input #code, winbone
Line Input #code, winbtwo
Line Input #code, winbthree
Line Input #code, winbfour
button #win.button, ""; winbtext$, [WinButtonClick], UL, winbone, winbtwo, winbthree, winbfour
return

[WinButton2]
Line Input #code, winbtexttwo$
Line Input #code, winbonetwo
Line Input #code, winbtwotwo
Line Input #code, winbthreetwo
Line Input #code, winbfourtwo
button #win.button2, ""; winbtexttwo$, [WinButtonClick2], UL, winbonetwo, winbtwotwo, winbthreetwo, winbfourtwo
return

[WinButton3]
Line Input #code, winbtextthree$
Line Input #code, winbonethree
Line Input #code, winbtwothree
Line Input #code, winbthreethree
Line Input #code, winbfourthree
button #win.button3, ""; winbtextthree$, [WinButtonClick3], UL, winbonethree, winbtwothree, winbthreethree, winbfourthree
return

[WinButton4]
Line Input #code, winbtextfour$
Line Input #code, winbonefour
Line Input #code, winbtwofour
Line Input #code, winbthreefour
Line Input #code, winbfourfour
button #win.button4, ""; winbtextfour$, [WinButtonClick4], UL, winbonefour, winbtwofour, winbthreefour, winbfourfour
return

[WinButton5]
Line Input #code, winbtextfive$
Line Input #code, winbonefive
Line Input #code, winbtwofive
Line Input #code, winbthreefive
Line Input #code, winbfourfive
button #win.button5, ""; winbtextfive$, [WinButtonClick5], UL, winbonefive, winbtwofive, winbthreefive, winbfourfive
return

[OnclickEvents]
if boct$ = "varone" then boct$ = varone$
if boct$ = "vartwo" then boct$ = vartwo$
if boct$ = "varthree" then boct$ = varthree$
if boct$ = "varfour" then boct$ = varfour$
if boct$ = "varfive" then boct$ = varfive$
if bocw$ = "varone" then bocw$ = varone$
if bocw$ = "vartwo" then bocw$ = vartwo$
if bocw$ = "varthree" then bocw$ = varthree$
if bocw$ = "varfour" then bocw$ = varfour$
if bocw$ = "varfive" then bocw$ = varfive$
if boce$ = "notice" then gosub [Notice]
if boce$ = "print textbox" then gosub [BOCPT]
if boce$ = "print textboxtwo" then gosub [BOCPT2]
if boce$ = "print textboxthree" then gosub [BOCPT3]
if boce$ = "print textboxfour" then gosub [BOCPT4]
if boce$ = "print textboxfive" then gosub [BOCPT5]
if boce$ = "print textedit" then gosub [BOCT]
if boce$ = "print textedittwo" then gosub [BOCT2]
if boce$ = "print texteditthree" then gosub [BOCT3]
if boce$ = "print texteditfour" then gosub [BOCT4]
if boce$ = "print texteditfive" then gosub [BOCT5]
if boce$ = "printer textbox" then gosub [BOCPTP]
if boce$ = "printer textboxtwo" then gosub [BOCPTP2]
if boce$ = "printer textboxthree" then gosub [BOCPTP3]
if boce$ = "printer textboxfour" then gosub [BOCPTP4]
if boce$ = "printer textboxfive" then gosub [BOCPTP5]
if boce$ = "printer textedit" then gosub [BOCTP]
if boce$ = "printer textedittwo" then gosub [BOCTP2]
if boce$ = "printer texteditthree" then gosub [BOCTP3]
if boce$ = "printer texteditfour" then gosub [BOCTP4]
if boce$ = "printer texteditfive" then gosub [BOCTP5]
if boce$ = "write file" then gosub [BOCWF]
if boce$ = "append file" then gosub [BOCAPF]
if boce$ = "playwav" then gosub [BOCPW]
if boce$ = "stopwav" then gosub [BOCSW]
if boce$ = "print" then gosub [BOCP]
if boce$ = "delete" then gosub [BOCD]
if boce$ = "internet" then gosub [BOCI]
if boce$ = "email" then gosub [BOCE]
if boce$ = "ascii" then gosub [BOCA]
if boce$ = "beep" then gosub [BOCB]
if boce$ = "close window" then gosub [BOCCW]
if boce$ = "cursor" then gosub [BOCCC]
if boce$ = "date" then gosub [BOCDD]
if boce$ = "drives" then gosub [BOCDDD]
if boce$ = "filedialog" then gosub [BOCF]
if boce$ = "makedir" then gosub [BOCMD]
if boce$ = "removedir" then gosub [BOCRD]
if boce$ = "printerdialog" then gosub [BOCPP]
if boce$ = "run" then gosub [BOCR]
if boce$ = "time" then gosub [BOCTT]
if boce$ = "run text" then gosub [BOCRT]
if boce$ = "fontdialog" then gosub [BOCFD]
if boce$ = "cd open" then gosub [DLLCDO]
if boce$ = "cd close" then gosub [DLLCDC]
if boce$ = "play avi" then gosub [BDLLPA]
if boce$ = "play avi fullscreen" then gosub [BDLLPAF]
if boce$ = "restart" then gosub [DLLR]
if boce$ = "swap mouse" then gosub [DLLSM]
if boce$ = "swap mouse back" then gosub [DLLSMB]
if boce$ = "read file textedit" then gosub [BOCRFT]
if boce$ = "read file textedittwo" then gosub [BOCRFT2]
if boce$ = "read file texteditthree" then gosub [BOCRFT3]
if boce$ = "read file texteditfour" then gosub [BOCRFT4]
if boce$ = "read file texteditfive" then gosub [BOCRFT5]
if boce$ = "play mp3" then gosub [BOCPMP3]
if boce$ = "stop music" then gosub [BOCPSMP3]
if boce$ = "pause music" then gosub [BOCPPMP3]
if boce$ = "play midi" then gosub [BOCPMIDI]
if boce$ = "colordialog" then gosub [BOCCD]
if boce$ = "download file" then gosub [BOCDF]
if boce$ = "textedit file" then gosub [BOCTF]
if boce$ = "textedittwo file" then gosub [BOCTF2]
if boce$ = "texteditthree file" then gosub [BOCTF3]
if boce$ = "texteditfour file" then gosub [BOCTF4]
if boce$ = "texteditfive file" then gosub [BOCTF]
if boce$ = "textbox file" then gosub [BOCTBF]
if boce$ = "textboxtwo file" then gosub [BOCTBF2]
if boce$ = "textboxthree file" then gosub [BOCTBF3]
if boce$ = "textboxfour file" then gosub [BOCTBF4]
if boce$ = "textboxfive file" then gosub [BOCTBF5]
if boce$ = "play mpeg" then gosub [BOCPMG]
if boce$ = "play mpeg fullscreen" then gosub [BOCPMGF]
if boce$ = "pause video" then gosub [BOCPPMG]
if boce$ = "stop video" then gosub [BOCPSMG]
if boce$ = "change window title" then gosub [BOCCWT]
if boce$ = "file check" then gosub [BOCFC]
if boce$ = "varone prompt" then gosub [BOCV1]
if boce$ = "vartwo prompt" then gosub [BOCV2]
if boce$ = "varthree prompt" then gosub [BOCV3]
if boce$ = "varfour prompt" then gosub [BOCV4]
if boce$ = "varfive prompt" then gosub [BOCV5]
if boce$ = "change text" then gosub [ChaText]
if boce$ = "change texttwo" then gosub [ChaText2]
if boce$ = "change textthree" then gosub [ChaText3]
if boce$ = "change textfour" then gosub [ChaText4]
if boce$ = "change textfive" then gosub [ChaText5]
if boce$ = "maximize" then gosub [BOCMAX]
if boce$ = "minimize" then gosub [BOCMIN]
goto [Loop2]

[WinButtonClick]
boce$=boceone$
boct$=boctone$
bocw$=bocwone$
goto [OnclickEvents]

[WinButtonClick2]
boce$=bocetwo$
boct$=bocttwo$
bocw$=bocwtwo$
goto [OnclickEvents]

[WinButtonClick3]
boce$=bocethree$
boct$=boctthree$
bocw$=bocwthree$
goto [OnclickEvents]

[WinButtonClick4]
boce$=bocefour$
boct$=boctfour$
bocw$=bocwfour$
goto [OnclickEvents]

[WinButtonClick5]
boce$=bocefive$
boct$=boctfive$
bocw$=bocwfive$
goto [OnclickEvents]

[WinBmpButton]
Line Input #code, winbb$
Line Input #code, winbbone
Line Input #code, winbbtwo
bmpbutton #win.bmpbutton, ""; winbb$, [WinBBClick], UL, winbbone, winbbtwo
return

[WinBmpButton2]
Line Input #code, winbbtwo$
Line Input #code, winbbonetwo
Line Input #code, winbbtwotwo
bmpbutton #win.bmpbutton2, ""; winbbtwo$, [WinBBClick2], UL, winbbonetwo, winbbtwotwo
return

[WinBmpButton3]
Line Input #code, winbbthree$
Line Input #code, winbbonethree
Line Input #code, winbbtwothree
bmpbutton #win.bmpbutton3, ""; winbbthree$, [WinBBClick3], UL, winbbonethree, winbbtwothree
return

[WinBmpButton4]
Line Input #code, winbbfour$
Line Input #code, winbbonefour
Line Input #code, winbbtwofour
bmpbutton #win.bmpbutton4, ""; winbbfour$, [WinBBClick4], UL, winbbonefour, winbbtwofour
return

[WinBmpButton5]
Line Input #code, winbbfive$
Line Input #code, winbbonefive
Line Input #code, winbbtwofive
bmpbutton #win.bmpbutton5, ""; winbbfive$, [WinBBClick5], UL, winbbonefive, winbbtwofive
return

[WinBBClick]
boce$=bboce$
boct$=bboct$
bocw$=bbocw$
goto [OnclickEvents]

[WinBBClick2]
boce$=bbocetwo$
boct$=bbocttwo$
bocw$=bbocwtwo$
goto [OnclickEvents]

[WinBBClick3]
boce$=bbocethree$
boct$=bboctthree$
bocw$=bbocwthree$
goto [OnclickEvents]

[WinBBClick4]
boce$=bbocefour$
boct$=bboctfour$
bocw$=bbocwfour$
goto [OnclickEvents]

[WinBBClick5]
boce$=bbocefive$
boct$=bboctfive$
bocw$=bbocwfive$
goto [OnclickEvents]

[WinListBox]
Line Input #code, winlone
Line Input #code, winltwo
Line Input #code, winlthree
Line Input #code, winlfour
listbox #win.listbox, array$(, [ListboxDoubleClick], winlone, winltwo, winlthree, winlfour
return

[ListboxDoubleClick]
print #win.listbox, "selectionindex? listindex"
if listindex=1 then goto [WinListbox1]
if listindex=2 then goto [WinListbox2]
if listindex=3 then goto [WinListbox3]
if listindex=4 then goto [WinListbox4]
if listindex=5 then goto [WinListbox5]
goto [Loop2]

[WinComboBox]
Line Input #code, wincone
Line Input #code, winctwo
Line Input #code, wincthree
Line Input #code, wincfour
combobox #win.combobox, array2$(, [ComboboxDoubleClick], wincone, winctwo, wincthree, wincfour
return

[ComboboxDoubleClick]
print #win.combobox, "selectionindex? index"
if index=1 then goto [WinCombobox1]
if index=2 then goto [WinCombobox2]
if index=3 then goto [WinCombobox3]
if index=4 then goto [WinCombobox4]
if index=5 then goto [WinCombobox5]
goto [Loop2]

[WinRadioButton]
Line Input #code, winrtext$
Line Input #code, winrone
Line Input #code, winrtwo
Line Input #code, winrthree
Line Input #code, winrfour
radiobutton #win.radiobutton, ""; winrtext$, [RadioButtonSet], [RadioButtonReset], winrone, winrtwo, winrthree, winrfour
return

[WinRadioButton2]
Line Input #code, winrtexttwo$
Line Input #code, winronetwo
Line Input #code, winrtwotwo
Line Input #code, winrthreetwo
Line Input #code, winrfourtwo
radiobutton #win.radiobutton2, ""; winrtexttwo$, [RadioButtonSet2], [RadioButtonReset], winronetwo, winrtwotwo, winrthreetwo, winrfourtwo
return

[WinRadioButton3]
Line Input #code, winrtextthree$
Line Input #code, winronethree
Line Input #code, winrtwothree
Line Input #code, winrthreethree
Line Input #code, winrfourthree
radiobutton #win.radiobutton3, ""; winrtextthree$, [RadioButtonSet3], [RadioButtonReset], winronethree, winrtwothree, winrthreethree, winrfourthree
return

[WinRadioButton4]
Line Input #code, winrtextfour$
Line Input #code, winronefour
Line Input #code, winrtwofour
Line Input #code, winrthreefour
Line Input #code, winrfourfour
radiobutton #win.radiobutton4, ""; winrtextfour$, [RadioButtonSet4], [RadioButtonReset], winronefour, winrtwofour, winrthreefour, winrfourfour
return

[WinRadioButton5]
Line Input #code, winrtextfive$
Line Input #code, winronefive
Line Input #code, winrtwofive
Line Input #code, winrthreefive
Line Input #code, winrfourfive
radiobutton #win.radiobutton5, ""; winrtextfive$, [RadioButtonSet5], [RadioButtonReset], winronefive, winrtwofive, winrthreefive, winrfourfive
return

[RadioButtonSet]
boce$=rboce$
boct$=rboct$
bocw$=rbocw$
goto [OnclickEvents]

[RadioButtonSet2]
boce$=rbocetwo$
boct$=rbocttwo$
bocw$=rbocwtwo$
goto [OnclickEvents]

[RadioButtonSet3]
boce$=rbocethree$
boct$=rboctthree$
bocw$=rbocwthree$
goto [OnclickEvents]

[RadioButtonSet4]
boce$=rbocefour$
boct$=rboctfour$
bocw$=rbocwfour$
goto [OnclickEvents]

[RadioButtonSet5]
boce$=rbocefive$
boct$=rboctfive$
bocw$=rbocwfive$
goto [OnclickEvents]

[RadioButtonReset]
goto [Loop2]

[WinCheckBox]
Line Input #code, wincboxtext$
Line Input #code, wincboxone
Line Input #code, wincboxtwo
Line Input #code, wincboxthree
Line Input #code, wincboxfour
checkbox #win.checkbox, ""; wincboxtext$, [CheckboxSet], [CheckboxReset], wincboxone, wincboxtwo, wincboxthree, wincboxfour
return

[WinCheckBox2]
Line Input #code, wincboxtexttwo$
Line Input #code, wincboxonetwo
Line Input #code, wincboxtwotwo
Line Input #code, wincboxthreetwo
Line Input #code, wincboxfourtwo
checkbox #win.checkbox2, ""; wincboxtexttwo$, [CheckboxSet2], [CheckboxReset], wincboxonetwo, wincboxtwotwo, wincboxthreetwo, wincboxfourtwo
return

[WinCheckBox3]
Line Input #code, wincboxtextthree$
Line Input #code, wincboxonethree
Line Input #code, wincboxtwothree
Line Input #code, wincboxthreethree
Line Input #code, wincboxfourthree
checkbox #win.checkbox3, ""; wincboxtextthree$, [CheckboxSet3], [CheckboxReset], wincboxonethree, wincboxtwothree, wincboxthreethree, wincboxfourthree
return

[WinCheckBox4]
Line Input #code, wincboxtextfour$
Line Input #code, wincboxonefour
Line Input #code, wincboxtwofour
Line Input #code, wincboxthreefour
Line Input #code, wincboxfourfour
checkbox #win.checkbox4, ""; wincboxtextfour$, [CheckboxSet4], [CheckboxReset], wincboxonefour, wincboxtwofour, wincboxthreefour, wincboxfourfour
return

[WinCheckBox5]
Line Input #code, wincboxtextfive$
Line Input #code, wincboxonefive
Line Input #code, wincboxtwofive
Line Input #code, wincboxthreefive
Line Input #code, wincboxfourfive
checkbox #win.checkbox5, ""; wincboxtextfive$, [CheckboxSet5], [CheckboxReset], wincboxonefive, wincboxtwofive, wincboxthreefive, wincboxfourfive
return

[CheckboxSet]
boce$=cboce$
boct$=cboct$
bocw$=cbocw$
goto [OnclickEvents]

[CheckboxSet2]
boce$=cbocetwo$
boct$=cbocttwo$
bocw$=cbocwtwo$
goto [OnclickEvents]

[CheckboxSet3]
boce$=cbocethree$
boct$=cboctthree$
bocw$=cbocwthree$
goto [OnclickEvents]

[CheckboxSet4]
boce$=cbocefour$
boct$=cboctfour$
bocw$=cbocwfour$
goto [OnclickEvents]

[CheckboxSet5]
boce$=cbocefive$
boct$=cboctfive$
bocw$=cbocwfive$
goto [OnclickEvents]


[CheckboxReset]
goto [Loop2]

[WinGroupBox]
Line Input #code, wingtext$
Line Input #code, wingone
Line Input #code, wingtwo
Line Input #code, wingthree
Line Input #code, wingfour
groupbox #win.groupbox, ""; wingtext$, wingone, wingtwo, wingthree, wingfour
return

[WinGroupBox2]
Line Input #code, wingtexttwo$
Line Input #code, wingonetwo
Line Input #code, wingtwotwo
Line Input #code, wingthreetwo
Line Input #code, wingfourtwo
groupbox #win.groupbox2, ""; wingtexttwo$, wingonetwo, wingtwotwo, wingthreetwo, wingfourtwo
return

[WinGroupBox3]
Line Input #code, wingtextthree$
Line Input #code, wingonethree
Line Input #code, wingtwothree
Line Input #code, wingthreethree
Line Input #code, wingfourthree
groupbox #win.groupbox3, ""; wingtextthree$, wingonethree, wingtwothree, wingthreethree, wingfourthree
return

[WinGroupBox4]
Line Input #code, wingtextfour$
Line Input #code, wingonefour
Line Input #code, wingtwofour
Line Input #code, wingthreefour
Line Input #code, wingfourfour
groupbox #win.groupbox4, ""; wingtextfour$, wingonefour, wingtwofour, wingthreefour, wingfourfour
return

[WinGroupBox5]
Line Input #code, wingtextfive$
Line Input #code, wingonefive
Line Input #code, wingtwofive
Line Input #code, wingthreefive
Line Input #code, wingfourfive
groupbox #win.groupbox5, ""; wingtextfive$, wingonefive, wingtwofive, wingthreefive, wingfourfive
return

[WinMenu]
menu #win, "&Menu", "&Click Here", [WinMenuClick]
return

[WinMenuClick]
boce$=mboce$
boct$=mboct$
bocw$=mbocw$
goto [OnclickEvents]

[WinLP]
Line Input #code, winlpone$
array$(0) = ""; winlpone$
return

[WinLP2]
Line Input #code, winlponetwo$
array$(1) = ""; winlponetwo$
return

[WinLP3]
Line Input #code, winlponethree$
array$(2) = ""; winlponethree$
return

[WinLP4]
Line Input #code, winlponefour$
array$(3) = ""; winlponefour$
return

[WinLP5]
Line Input #code, winlponefive$
array$(4) = ""; winlponefive$
return

[WinCP]
Line Input #code, wincpone$
array2$(0) = ""; wincpone$
return

[WinCP2]
Line Input #code, wincponetwo$
array2$(1) = ""; wincponetwo$
return

[WinCP3]
Line Input #code, wincponethree$
array2$(2) = ""; wincponethree$
return

[WinCP4]
Line Input #code, wincponefour$
array2$(3) = ""; wincponefour$
return

[WinCP5]
Line Input #code, wincponefive$
array2$(4) = ""; wincponefive$
return

[BOC]
Line Input #code, boceone$
Line Input #code, boctone$
Line Input #code, bocwone$
return

[BOC2]
Line Input #code, bocetwo$
Line Input #code, bocttwo$
Line Input #code, bocwtwo$
return

[BOC3]
Line Input #code, bocethree$
Line Input #code, boctthree$
Line Input #code, bocwthree$
return

[BOC4]
Line Input #code, bocefour$
Line Input #code, boctfour$
Line Input #code, bocwfour$
return

[BOC5]
Line Input #code, bocefive$
Line Input #code, boctfive$
Line Input #code, bocwfive$
return

[Notice]
notice ""; boct$
return

[BOCPT]
print #win.textbox, ""; boct$
return

[BOCPT2]
print #win.textbox2, ""; boct$
return

[BOCPT3]
print #win.textbox3, ""; boct$
return

[BOCPT4]
print #win.textbox4, ""; boct$
return

[BOCPT5]
print #win.textbox5, ""; boct$
return

[BOCPTP]
print #win.textbox, "!contents?"
input #win.textbox, printingtext$
lprint ""; printingtext$
dump
return

[BOCPTP2]
print #win.textbox2, "!contents?"
input #win.textbox2, printingtext$
lprint ""; printingtext$
dump
return

[BOCPTP3]
print #win.textbox3, "!contents?"
input #win.textbox3, printingtext$
lprint ""; printingtext$
dump
return

[BOCPTP4]
print #win.textbox4, "!contents?"
input #win.textbox4, printingtext$
lprint ""; printingtext$
dump
return

[BOCPTP5]
print #win.textbox5, "!contents?"
input #win.textbox5, printingtext$
lprint ""; printingtext$
dump
return

[Error]
notice "No code in editor!"
goto [Loop]

[BOCT]
print #win.textedit, ""; boct$
return

[BOCT2]
print #win.textedit2, ""; boct$
return

[BOCT3]
print #win.textedit3, ""; boct$
return

[BOCT4]
print #win.textedit4, ""; boct$
return

[BOCT5]
print #win.textedit5, ""; boct$
return

[BOCTP]
print #win.textedit, "!selectall" ;
print #win.textedit, "!contents?"
input #win.textedit, printingtext$
lprint ""; printingtext$
dump
return

[BOCTP2]
print #win.textedit2, "!selectall" ;
print #win.textedit2, "!contents?"
input #win.textedit2, printingtext$
lprint ""; printingtext$
dump
return

[BOCTP3]
print #win.textedit3, "!selectall" ;
print #win.textedit3, "!contents?"
input #win.textedit3, printingtext$
lprint ""; printingtext$
dump
return

[BOCTP4]
print #win.textedit4, "!selectall" ;
print #win.textedit4, "!contents?"
input #win.textedit4, printingtext$
lprint ""; printingtext$
dump
return

[BOCTP5]
print #win.textedit5, "!selectall" ;
print #win.textedit5, "!contents?"
input #win.textedit5, printingtext$
lprint ""; printingtext$
dump
return

[BOCWF]
open ""; boct$ for output as #bocf
print #bocf, ""; bocw$
close #bocf
return

[BOCPW]
playwave ""; boct$, async
return

[BOCSW]
playwave ""
return

[BOCP]
lprint ""; boct$
dump
return

[BOCD]
kill ""; boct$
return

[BOCI]
url$ = ""; boct$
gosub [Go]
return

[Go]
h = 0
lpOperation$ = "open" + chr$(0)
lpFile$ = url$ + chr$(0)
lpParameters$ = "" + chr$(0)
lpDirectory$ = "" + chr$(0)
nShowCmd = _SW_SHOW

open "shell32.dll" for dll as #shell

calldll #shell, "ShellExecuteA", _
h as word, _
lpOperation$ as ptr, _
lpFile$ as ptr, _
lpParameters$ as ptr, _
lpDirectory$ as ptr, _
nShowCmd as short, _
result as word
close #shell
if result < 32 then notice "Error!"
return

[BOCE]
gosub [Go2]
return

[Go2]
lpOperation$ = "open" + chr$(0)
lpFile$ ="mailto:"; boct$+ chr$(0)
lpParameters$ = "" + chr$(0)
lpDirectory$ = "" + chr$(0)
nShowCmd = _SW_SHOWNORMAL

open "shell32.dll" for dll as #shell

calldll #shell, "ShellExecuteA", _
h as word, _
lpOperation$ as ptr, _
lpFile$ as ptr, _
lpParameters$ as ptr, _
lpDirectory$ as ptr, _
nShowCmd as short, _
result as word
close #shell
if result < 32 then notice "Error!"
return

[BOCA]
notice asc( boct$ )
return

[BOCB]
beep
return

[BOCCW]
close #win
return

[BOCCC]
if boct$ = "normal" then cursor normal
if boct$ = "arrow" then cursor arrow
if boct$ = "crosshair" then cursor crosshair
if boct$ = "hourglass" then cursor hourglass
if boct$ = "text" then cursor text
return

[BOCDD]
d$ = date$()
notice d$
return

[BOCDDD]
notice Drives$
return

[BOCF]
filedialog "Files", "*.*", fileName$
return

[BOCMD]
result = mkdir( boct$ )
return

[BOCPP]
printerdialog
return

[BOCR]
run boct$
return

[BOCTT]
notice ""; amPmTime$(time$())
return

[BOCRT]
run "notepad "; boct$
return

[BBOC]
Line Input #code, bboce$
Line Input #code, bboct$
Line Input #code, bbocw$
return

[BBOC2]
Line Input #code, bbocetwo$
Line Input #code, bbocttwo$
Line Input #code, bbocwtwo$
return

[BBOC3]
Line Input #code, bbocethree$
Line Input #code, bboctthree$
Line Input #code, bbocwthree$
return

[BBOC4]
Line Input #code, bbocefour$
Line Input #code, bboctfour$
Line Input #code, bbocwfour$
return

[BBOC5]
Line Input #code, bbocefive$
Line Input #code, bboctfive$
Line Input #code, bbocwfive$
return

[RBOC]
Line Input #code, rboce$
Line Input #code, rboct$
Line Input #code, rbocw$
return

[RBOC2]
Line Input #code, rbocetwo$
Line Input #code, rbocttwo$
Line Input #code, rbocwtwo$
return

[RBOC3]
Line Input #code, rbocethree$
Line Input #code, rboctthree$
Line Input #code, rbocwthree$
return

[RBOC4]
Line Input #code, rbocefour$
Line Input #code, rboctfour$
Line Input #code, rbocwfour$
return

[RBOC5]
Line Input #code, rbocefive$
Line Input #code, rboctfive$
Line Input #code, rbocwfive$
return

[CBOC]
Line Input #code, cboce$
Line Input #code, cboct$
Line Input #code, cbocw$
return

[CBOC2]
Line Input #code, cbocetwo$
Line Input #code, cbocttwo$
Line Input #code, cbocwtwo$
return

[CBOC3]
Line Input #code, cbocethree$
Line Input #code, cboctthree$
Line Input #code, cbocwthree$
return

[CBOC4]
Line Input #code, cbocefour$
Line Input #code, cboctfour$
Line Input #code, cbocwfour$
return

[CBOC5]
Line Input #code, cbocefive$
Line Input #code, cboctfive$
Line Input #code, cbocwfive$
return

[MBOC]
Line Input #code, mboce$
Line Input #code, mboct$
Line Input #code, mbocw$
return

[BackgroundColor]
Line Input #code, backcolor$
backcheck$ = "continue"
return

[TextboxColor]
Line Input #code, textbcolor$
TextboxColor$ = ""; textbcolor$
return

[TexteditColor]
Line Input #code, textecolor$
TexteditorColor$ = ""; textecolor$
return

[ComboboxColor]
Line Input #code, combobcolor$
ComboboxColor$ = ""; combobcolor$
return

[ListboxColor]
Line Input #code, listbcolor$
ListboxColor$ = ""; listbcolor$
return

[GetBackgroundColor]
backcolor$ = "buttonface"
return

[BOCFD]
fontdialog "courier_new 10 bold italic", newFontSpec$
return

[PrintTextW]
Line Input #code, textfortext$
textcontinue$ = "continue"
return

[TPP]
Line Input #code, tppevent$
tppcontinue$ = "continue"
return

[OpenPMP3]
Line Input #code, openpmp3$
openmp3continue$ = "continue"
return

[TPC]
Line Input #code, tpcevent$
tpcconfirm$ = "continue"
return

[OpenFile]
filedialog "Open Program...","*.lep",fileName$
if fileName$ = "" then goto [Loop]
open ""; fileName$ for input as #openf
print #main.text, "!contents #openf";
close #openf
fileName$=lower$(fileName$)
NewText$ = "Leopard - "; fileName$
calldll #user, "SetWindowTextA",_
z as word,_
NewText$ as ptr,_
result as void
goto [Loop]

[SaveFile]
quitanswer$ = "no"
filedialog "Save Program...","*.lep",save$
if save$ = "" then goto [Loop]
open ""; save$ for output as #save
print #main.text, "!selectall" ;
print #main.text, "!copy" ;
print #main.text, "!contents?"
input #main.text, code2$
print #save, code2$
close #save
save$=lower$(save$)
NewText3$ = "Leopard - "; save$
calldll #user, "SetWindowTextA",_
z as word,_
NewText3$ as ptr,_
result as void
goto [Loop]

[CompileFile]
prompt "Please enter program name..." ; programname$
if programname$ = "" then goto [Loop]
open "program.dat" for output as #compilerfile
print #compilerfile, ""; programname$
close #compilerfile
notice "Finished!"
goto [Loop]

[PrintCode]
print #main.text, "!contents?"
input #main.text, code2$
if code2$ = "" then goto [NoCode]
lprint "Leopard Program"
lprint ""
d$ = date$()
lprint ""; d$
lprint ""; amPmTime$(time$())
lprint ""
lprint "----------------------------------------"
lprint ""
lprint ""; code2$
dump
goto [Loop]

[ChangeFont]
fontdialog ""; specifiedfont$, newFont$
print #main.text, "!font "; newFont$
open "font.dat" for output as #fontchange
print #fontchange, ""; newFont$
close #fontchange
goto [Loop]

[HelpTopics]
run "notepad readme.txt"
goto [Loop]

[AboutLeopard]
'DO NOT EDIT OR REMOVE THE INFORMATION CONTAINED HERE!
notice "About Leopard" + chr$(13) + chr$(13) + "Leopard - Created by Brandon Watts" + chr$(13) + "Web Site - http://www.leopardprogramming.com" + chr$(13) + "E-mail - brandonwatts@adelphia.net" + chr$(13) + chr$(13) + "This work is licensed under the CC-GNU GPL."
goto [Loop]

[DLLCDO]
calldll #mm,"mciSendStringA",_
"set cdaudio door open" as ptr,_
0 as long,0 as short,0 as short, result as long
return

[DLLCDC]
calldll #mm,"mciSendStringA",_
"set cdaudio door closed" as ptr,_
0 as long,0 as short,0 as short, result as long
return

[BDLLPA]
boct$=GetShortPathName$(boct$)
r$=mciSendString$("open "+boct$+" type avivideo alias movie")
r$=mciSendString$("play movie")
return

Function mciSendString$(s$)
buffer$=space$(1024)+chr$(0)
calldll #mm,"mciSendStringA",s$ as ptr,buffer$ as ptr,_
1028 as short, 0 as short, r as long

buffer$=left$(buffer$, instr(buffer$, chr$(0)) - 1)
if r>0 then
mciSendString$="error"
else
mciSendString$=buffer$
end if
End Function

Function GetShortPathName$(lPath$)
lPath$=lPath$+chr$(0)
sPath$=space$(256)
lenPath=len(sPath$)
open "kernel32" for dll as #k
calldll #k, "GetShortPathNameA",lPath$ as ptr,_
sPath$ as ptr,lenPath as long,r as long
close #k
GetShortPathName$=left$(sPath$,r)
end function
close #k
return

[DLLR]
dwReserved$ = "_EW_REBOOTSYSTEM"
calldll #user, "ExitWindows", _
dwReserved$ as long, _
wReturnCode as word, _
result as short
close #user
end

[DLLSM]
calldll #user, "SwapMouseButton", _
1 as ushort, _
result as void
return

[DLLSMB]
calldll #user, "SwapMouseButton", _
0 as ushort, _
result as void
return

[ChangeTextColor]
prompt "Please type the font color... (example: green)" ; fontcolorchoice$
open "pref.dat" for output as #forecolor
if fontcolorchoice$ = "" then fontcolorchoice$ = "blue"
fontcolorchoice$=lower$(fontcolorchoice$)
print #forecolor, ""; fontcolorchoice$
close #forecolor
goto [Loop]

[BOCRFT]
open ""; boct$ for input as #bocrft
print #win.textedit, "!contents #bocrft";
close #bocrft
return

[BOCRFT2]
open ""; boct$ for input as #bocrft
print #win.textedit2, "!contents #bocrft";
close #bocrft
return

[BOCRFT3]
open ""; boct$ for input as #bocrft
print #win.textedit3, "!contents #bocrft";
close #bocrft
return

[BOCRFT4]
open ""; boct$ for input as #bocrft
print #win.textedit, "!contents #bocrft";
close #bocrft
return

[BOCRFT5]
open ""; boct$ for input as #bocrft
print #win.textedit5, "!contents #bocrft";
close #bocrft
return

[BOCPMP3]
r$=mciSendStringA$("open "+boct$+" type MpegVideo alias music")
r$=mciSendStringA$("play music")
return

[PlayIt]
r$=mciSendStringA$("open "+openpmp3$+" type MpegVideo alias music")
r$=mciSendStringA$("play music")
return

[BOCPSMP3]
r$=mciSendStringA$("close music")
return

[BOCPPMP3]
r$=mciSendStringA$("pause music")
return

Function mciSendStringA$(s$)
buffer$=space$(1024)+chr$(0)
calldll #mm,"mciSendStringA",s$ as ptr,buffer$ as ptr,_
1028 as short, 0 as short, r as long

buffer$=left$(buffer$, instr(buffer$, chr$(0)) - 1)
if r>0 then
mciSendString$="error"
else
mciSendString$=buffer$
end if
End Function

[BOCPMIDI]
r$=mciSendStringA$("open "+boct$+" type sequencer alias music")
r$=mciSendStringA$("play music")
return

[BOCCD]
colordialog boct$, r$
return

[BDLLPAF]
r$=mciSendStringA$("open "+boct$+" type avivideo alias movie style popup")
r$=mciSendStringA$("put movie window at 0 0 ";DisplayWidth;" ";DisplayHeight)
r$=mciSendStringA$("play movie wait")
r$=mciSendStringA$("close movie")
wait
return

[EndProblem]
close #code
notice "No 'end' command!"
goto [Loop]

[BOCDF]
open "URLmon" for dll as #url

urlfile$ = ""; boct$
localfile$ = ""; bocw$

calldll #url, "URLDownloadToFileA",_
0 as long,_
urlfile$ as ptr,_
localfile$ as ptr,_
0 as long, 0 as long, ret as long

close #url
return

[BOCTF]
print #win.textedit, "!selectall" ;
print #win.textedit, "!copy" ;
print #win.textedit, "!contents?"
input #win.textedit, boctff$
open ""; boct$ for append as #boctff
print #boctff, ""; boctff$
close #boctff
return

[BOCTF2]
print #win.textedit2, "!selectall" ;
print #win.textedit2, "!copy" ;
print #win.textedit2, "!contents?"
input #win.textedit2, boctff$
open ""; boct$ for append as #boctff
print #boctff, ""; boctff$
close #boctff
return

[BOCTF3]
print #win.textedit3, "!selectall" ;
print #win.textedit3, "!copy" ;
print #win.textedit3, "!contents?"
input #win.textedit3, boctff$
open ""; boct$ for append as #boctff
print #boctff, ""; boctff$
close #boctff
return

[BOCTF4]
print #win.textedit4, "!selectall" ;
print #win.textedit4, "!copy" ;
print #win.textedit4, "!contents?"
input #win.textedit4, boctff$
open ""; boct$ for append as #boctff
print #boctff, ""; boctff$
close #boctff
return

[BOCTF5]
print #win.textedit5, "!selectall" ;
print #win.textedit5, "!copy" ;
print #win.textedit5, "!contents?"
input #win.textedit5, boctff$
open ""; boct$ for append as #boctff
print #boctff, ""; boctff$
close #boctff
return

[BOCTBF]
print #win.textbox, "!contents?"
input #win.textbox, boctbff$
open ""; boct$ for append as #boctbff
print #boctbff, ""; boctbff$
close #boctbff
return

[BOCTBF2]
print #win.textbox2, "!contents?"
input #win.textbox2, boctbff$
open ""; boct$ for append as #boctbff
print #boctbff, ""; boctbff$
close #boctbff
return

[BOCTBF3]
print #win.textbox3, "!contents?"
input #win.textbox3, boctbff$
open ""; boct$ for append as #boctbff
print #boctbff, ""; boctbff$
close #boctbff
return

[BOCTBF4]
print #win.textbox4, "!contents?"
input #win.textbox4, boctbff$
open ""; boct$ for append as #boctbff
print #boctbff, ""; boctbff$
close #boctbff
return

[BOCTBF5]
print #win.textbox5, "!contents?"
input #win.textbox5, boctbff$
open ""; boct$ for append as #boctbff
print #boctbff, ""; boctbff$
close #boctbff
return

[BOCPMG]
r$=mciSendString$("open "+boct$+" type MpegVideo alias movie style popup")
r$=mciSendString$("play movie")
goto [Loop]

[BOCPPMG]
r$=mciSendString$("pause movie")
goto [Loop]

[BOCPSMG]
r$=mciSendString$("close movie")
goto [Loop]

[closemovie]
r$=mciSendString$("status movie position")
if val(r$)<mlength then [Loop]
r$=mciSendString$("close movie")
timer 0
movieOpen=0
return

[BOCPMGF]
r$=mciSendString$("open "+boct$+" type MPegvideo alias movie style popup")
r$=mciSendString$("put movie window at 0 0 ";DisplayWidth;" ";DisplayHeight)
r$=mciSendString$("play movie wait")
r$=mciSendString$("close movie")
goto [Loop]

[BlackText]
open "color.dat" for output as #forecolor
print #forecolor, "black"
close #forecolor
goto [Loop]

[BlueText]
open "color.dat" for output as #forecolor
print #forecolor, "blue"
close #forecolor
goto [Loop]

[BrownText]
open "color.dat" for output as #forecolor
print #forecolor, "brown"
close #forecolor
goto [Loop]

[ButtonfaceText]
open "color.dat" for output as #forecolor
print #forecolor, "buttonface"
close #forecolor
goto [Loop]

[CyanText]
open "color.dat" for output as #forecolor
print #forecolor, "cyan"
close #forecolor
goto [Loop]

[DarkBlueText]
open "color.dat" for output as #forecolor
print #forecolor, "darkblue"
close #forecolor
goto [Loop]

[DarkCyanText]
open "color.dat" for output as #forecolor
print #forecolor, "darkcyan"
close #forecolor
goto [Loop]

[DarkGrayText]
open "color.dat" for output as #forecolor
print #forecolor, "darkgray"
close #forecolor
goto [Loop]

[DarkGreenText]
open "color.dat" for output as #forecolor
print #forecolor, "darkgreen"
close #forecolor
goto [Loop]

[DarkPinkText]
open "color.dat" for output as #forecolor
print #forecolor, "darkpink"
close #forecolor
goto [Loop]

[DarkRedText]
open "color.dat" for output as #forecolor
print #forecolor, "darkred"
close #forecolor
goto [Loop]

[GreenText]
open "color.dat" for output as #forecolor
print #forecolor, "green"
close #forecolor
goto [Loop]

[LightGrayText]
open "color.dat" for output as #forecolor
print #forecolor, "lightgray"
close #forecolor
goto [Loop]

[PaleGrayText]
open "color.dat" for output as #forecolor
print #forecolor, "palegray"
close #forecolor
goto [Loop]

[PinkText]
open "color.dat" for output as #forecolor
print #forecolor, "pink"
close #forecolor
goto [Loop]

[RedText]
open "color.dat" for output as #forecolor
print #forecolor, "red"
close #forecolor
goto [Loop]

[YellowText]
open "color.dat" for output as #forecolor
print #forecolor, "yellow"
close #forecolor
goto [Loop]

function amPmTime$(time$)
colonIndex = instr(time$, ":")
hours = val(left$(time$, colonIndex - 1))
amOrPm$ = " AM"
if hours > 12 then
hours = hours - 12
amOrPm$ = " PM"
else
if hours = 0 then hours = 12
end if
amPmTime$ = str$(hours) + mid$(time$, colonIndex) + amOrPm$
end function

[CCOC]
Line Input #code, ccoceone$
Line Input #code, ccoctone$
Line Input #code, ccocwone$
return

[CCOC2]
Line Input #code, ccocetwo$
Line Input #code, ccocttwo$
Line Input #code, ccocwtwo$
return

[CCOC3]
Line Input #code, ccocethree$
Line Input #code, ccoctthree$
Line Input #code, ccocwthree$
return

[CCOC4]
Line Input #code, ccocefour$
Line Input #code, ccoctfour$
Line Input #code, ccocwfour$
return

[CCOC5]
Line Input #code, ccocefive$
Line Input #code, ccoctfive$
Line Input #code, ccocwfive$
return

[WinCombobox1]
boce$=ccoceone$
boct$=ccoctone$
bocw$=ccocwone$
goto [OnclickEvents]

[WinCombobox2]
boce$=ccocetwo$
boct$=ccocttwo$
bocw$=ccocwtwo$
goto [OnclickEvents]

[WinCombobox3]
boce$=ccocethree$
boct$=ccoctthree$
bocw$=ccocwthree$
goto [OnclickEvents]

[WinCombobox4]
boce$=ccocefour$
boct$=ccoctfour$
bocw$=ccocwfour$
goto [OnclickEvents]

[WinCombobox5]
boce$=ccocefive$
boct$=ccoctfive$
bocw$=ccocwfive$
goto [OnclickEvents]

[LCOC]
Line Input #code, lloceone$
Line Input #code, lloctone$
Line Input #code, llocwone$
return

[LCOC2]
Line Input #code, lloceonetwo$
Line Input #code, lloctonetwo$
Line Input #code, llocwonetwo$
return

[LCOC3]
Line Input #code, lloceonethree$
Line Input #code, lloctonethree$
Line Input #code, llocwonethree$
return

[LCOC4]
Line Input #code, lloceonefour$
Line Input #code, lloctonefour$
Line Input #code, llocwonefour$
return

[LCOC5]
Line Input #code, lloceonefive$
Line Input #code, lloctonefive$
Line Input #code, llocwonefive$
return

[WinListbox1]
boce$=lloceone$
boct$=lloctone$
bocw$=llocwone$
goto [OnclickEvents]

[WinListbox2]
boce$=lloceonetwo$
boct$=lloctonetwo$
bocw$=llocwonetwo$
goto [OnclickEvents]

[WinListbox3]
boce$=lloceonethree$
boct$=lloctonethree$
bocw$=llocwonethree$
goto [OnclickEvents]

[WinListbox4]
boce$=lloceonefour$
boct$=lloctonefour$
bocw$=llocwonefour$
goto [OnclickEvents]

[WinListbox5]
boce$=lloceonefive$
boct$=lloctonefive$
bocw$=llocwonefive$
goto [OnclickEvents]

[BOCCWT]
u = hwnd(#win)
calldll #user, "SetWindowTextA",_
u as word,_
boct$ as ptr,_
result as void
return

[BOCAPF]
open ""; boct$ for append as #bocf
print #bocf, ""; bocw$
close #bocf
return

[BOCRD]
result = rmdir( boct$ )
return

[Var1]
Line Input #code, varone$
return

[Var2]
Line Input #code, vartwo$
return

[Var3]
Line Input #code, varthree$
return

[Var4]
Line Input #code, varfour$
return

[Var5]
Line Input #code, varfive$
return

[BOCFC]
dim filec$(1, 1)
files "", boct$, filec$(
if val(filec$(0, 0)) > 0 then _
notice "File " + boct$ + " Exists" _
else _
notice "File " + boct$ + " Does Not Exist"
return

[BOCV1]
prompt boct$; varone$
return

[BOCV2]
prompt boct$; vartwo$
return

[BOCV3]
prompt boct$; varthree$
return

[BOCV4]
prompt boct$; varfour$
return

[BOCV5]
prompt boct$; varfive$
return

[TextOpenFile]
Line Input #code, textopenff$
textstartgo$="go"
return

[Proceed]
open ""; textopenff$ for input as #openedtext
print #win, "!contents #openedtext";
close #openedtext
return

[ChaText]
print #win.statictext, ""; boct$
return

[ChaText2]
print #win.statictext2, ""; boct$
return

[ChaText3]
print #win.statictext3, ""; boct$
return

[ChaText4]
print #win.statictext4, ""; boct$
return

[ChaText5]
print #win.statictext5, ""; boct$
return

[BOCMAX]
calldll #user32, "GetActiveWindow",hMain as ulong
CallDLL #user32, "ShowWindow",hMain As uLong,_
_SW_MAXIMIZE As Long, r As Boolean
return

[BOCMIN]
calldll #user32, "GetActiveWindow",hMain as ulong
CallDLL #user32, "ShowWindow",hMain As uLong,_
_SW_SHOWMINIMIZED As Long, r As Boolean
return

[PreMax]
maxcontinue$ = "continue"
return

[PreMin]
mincontinue$ = "continue"
return

[InvisWindow]
Line Input #code, boceone$
Line Input #code, boctone$
Line Input #code, bocwone$
close #code
goto [WinButtonClick]

[NoCode]
notice "No code in editor."
goto [Loop]


