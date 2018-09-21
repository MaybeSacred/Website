module QRGenerator 
open Suave.FunctionalViewEngine
open CommonHtml
open Suave.Utils.Crypto
open System.Text
open FSharpx
open Types
open System
open ZXing
open ZXing.QrCode
open System.Drawing.Imaging
open System.Drawing
open System.IO

let encode' size str =
    let writer = 
        new BarcodeWriterPixelData(
            Format = BarcodeFormat.QR_CODE,
            Options = new QrCodeEncodingOptions(Height=size, Width=size, Margin=5)
    )
    let data = writer.Write(contents=str)
    use bitmap = new Bitmap(data.Width, data.Height, PixelFormat.Format32bppRgb)
    use ms = new MemoryStream()
    let bmData = bitmap.LockBits(new Rectangle(0,0,data.Width,data.Height), ImageLockMode.WriteOnly, PixelFormat.Format32bppRgb)
    try 
        System.Runtime.InteropServices.Marshal.Copy(data.Pixels, 0, bmData.Scan0, data.Pixels.Length)
    finally
        bitmap.UnlockBits(bmData)
    bitmap.Save(ms, ImageFormat.Png)
    ms.ToArray() |> Convert.ToBase64String

let rand () = 
    let b = Array.zeroCreate<byte> 50
    cryptRandom.GetBytes b
    ASCIIEncoding.ASCII.GetString b

let base64Qr () = "data:image/gif;base64," + (rand () |> encode' 125)

let page = {
    Title = "QR Code Generator" 
    Created = DateTime.Now
    Modified = DateTime(2018, 2, 22)
    Content = Nodes (fun () ->
        [
        div [class' "container mx-auto"] [
            div [class' "row"] ([
                h3 [class' "col-12 text-center"] [rawText "QR Codes"]
                p [class' "col-12 text-center"] [rawText "12 Artisanal Hand-Crafted QR Codes"]
                br'
            ] |> flip List.append [for _ in 0 .. 11 do yield div [class' "col-12 col-md-6 col-lg-4 col-xl-2"] [img [class' "align-middle mx-auto d-block"; src <| base64Qr ()]] ])
        ]
    ] ) }

let ``making-a-qr-code-generator`` = { 
    Title = "QR Codes for Pokémon" 
    Created = DateTime(2018,20,9)
    Modified = DateTime(2018,20,9)
    Content = textify 
        [
            div [] [
                h2 [class' "text-center"] [rawText "Building a QR Generator for Pokémon"]
                br'
                a [title' "By en:Game Freak, en:Nintendo, en:The Pokémon Company (Transferred from en.wikipedia to Commons.) [Public domain], via Wikimedia Commons"; href "https://commons.wikimedia.org/wiki/File%3AInternational_Pok%C3%A9mon_logo.svg"; class' "img-responsive center-block"] [
                    img [attr "width" "256"; attr "alt" "International Pokémon logo"; src "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Pok%C3%A9mon_logo.svg/256px-International_Pok%C3%A9mon_logo.svg.png"]
                ]
                br'
                br'
                p [] [
                    rawText "   The newest generation of Pokémon games, "
                    a [href "https://www.serebii.net/ultrasunultramoon/"] [rawText "Sun and Moon and their Ultra counterparts"]
                    rawText """, have a 
                    feature where Pokémon not normally found within the game can be caught. This is called Island Scan, and each activation of Island Scan requires 
                    scanning QR codes using the Nintendo DS camera. The game designers were clever though, the 
                    game won't count scanning the same QR code multiple times, so you'll need many distinct codes if 
                    you intend to catch all 40ish Pokémon available through the Island Scan feature. This sounded like a fun little problem to solve and ultimately, 
                    solving it led to the creation of this site"""
                ]
                h4 [] [rawText "What's a poor programmer to do?"]
                paragraph """Make a randomized QR code generator, of course! TL;DR, That's exactly what I did. """
                // include hanselman article
                // https://www.hanselman.com/blog/HowDoYouUseSystemDrawingInNETCore.aspx?utm_source=csharpdigest&utm_medium=email&utm_campaign=featured
                // describe various attempts to get it working on Linux
                // include summary of the steps: install packages and install Linux libraries like from hanselman article
                // include building of api and query params
            ]
        ] }