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

let base64Qr () = "data:image/gif;base64," + (rand () |> encode' 120)

let page = {
    Title = "QR Code Generator" 
    Modified = DateTime(2018, 2, 22)
    Content = Nodes (fun () ->
        [
        div [class' "container mx-auto"] [
            div [class' "row"] [ 
                for _ in 0 .. 11 do yield div [class' "col-12 col-md-6 col-lg-4 col-xl-2"] [img [class' "align-middle mx-auto d-block"; src <| base64Qr ()]] 
            ]
        ]
    ] ) }