open System
open Newtonsoft.Json
open System.Threading
open Suave
open Suave.Filters
open Suave.Operators
open Suave.Successful
open Suave.Utils.Collections
open System.Text
open Suave.Writers
open System.IO
open Suave.FunctionalViewEngine
open System.Net
open Argu

let returnJson o = JsonConvert.SerializeObject o |> UTF8Encoding.UTF8.GetBytes |> ok >=> setMimeType "application/json; charset=utf-8"
let renderOK = renderHtmlDocument >> OK
let articles = 
    dict [
        "inaugaral", Articles.inaugaral
        "", Articles.main
]
type Arguments =
    | Port of UInt16
    interface IArgParserTemplate with
        member s.Usage =
            match s with
            | Port _ -> "the port to start the server listening on"

[<EntryPoint>]
let main argv = 
    let cts = new CancellationTokenSource()
    let app = 
        choose 
            [ GET >=> choose [
                path Paths.``base`` >=> request (fun _ -> Index.page () |> renderOK)
                path Paths.home >=> request (fun _ -> Index.page () |> renderOK)
                path Paths.sitemap >=> request (fun _ -> AllLinks.sitemap () |> renderOK)
                path Paths.``qr-generator`` >=> request (fun _ -> QRGenerator.page () |> renderOK)
                path Paths.about >=> request (fun _ -> About.about () |> renderOK)
                path Paths.``Jonny's Sober Rants`` >=> request (fun _ -> About.about () |> renderOK)
                path Paths.``license-generator`` >=> request (fun _ -> LicenseGenerator.page () |> renderOK)
                path Paths.``all-programming-links`` >=> request (fun _ -> AllLinks.``all-programming-links`` () |> renderOK)
                path Paths.``all-fun-links`` >=> request (fun _ -> AllLinks.``all-fun-links`` () |> renderOK)
                path Paths.``dev-random`` >=> request (fun _ -> Index.``dev\random`` () |> renderOK)
                path Paths.experimental >=> Files.browseFileHome "experimental.html"
                pathScan "/articles/%s" (fun x -> 
                    match articles.ContainsKey x with
                    | true -> articles.[x] () |> renderOK
                    | _ -> (fun _ -> async { return None })
                )
                path Paths.articles >=> request (fun _ -> Articles.main () |> renderOK)
                pathRegex "(.*)\.(css|png)" >=> Files.browseHome
              ]
              POST >=> choose [
                path "/hello" >=> OK "Hello Post"
                path "/goodbye" >=> OK "Good bye Post" 
              ]
              // TODO: add cutesy 404 page
              RequestErrors.NOT_FOUND "Uh oh! Looks like that page doesn't exist"
            ]
    let parser = ArgumentParser.Create<Arguments>(programName="Server.exe")
    let cliArgs = parser.Parse(argv, ignoreMissing=true, ignoreUnrecognized=true)
    let conf = { defaultConfig with 
                    cancellationToken = cts.Token; 
                    bindings = [cliArgs.GetResult(<@ Port @>, 8081us) |> HttpBinding.create HTTP IPAddress.Loopback ]
                    homeFolder = Some <| Path.GetFullPath( Path.Combine( __SOURCE_DIRECTORY__, """..\..\public""" ) ); }
    let listening, server = startWebServerAsync conf app
    Async.Start (server, cts.Token)
    // just use concurrent queue, with blocking for backpressure 
    let p = Console.Read ()
    cts.Cancel ()
    0 // return an integer exit code 
