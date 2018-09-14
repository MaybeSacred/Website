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
open NLog
open NLog.FSharp
open CommonHtml

let log = new Logger()
let returnJson o = JsonConvert.SerializeObject o |> UTF8Encoding.UTF8.GetBytes |> ok >=> setMimeType "application/json; charset=utf-8"
let renderTemplateOK = template >> renderHtmlDocument >> OK
let mainPages = [
    Paths.``base``, Index.page
    Paths.home, Index.page
    Paths.index, Index.page
    Paths.sitemap, AllLinks.sitemap
    Paths.``qr-generator``, QRGenerator.page
    Paths.about, About.about
    //Paths.``Jonny's Sober Rants``, About.about
    Paths.resume, Resume.page
    Paths.``all-programming-links``, AllLinks.``all-programming-links``
    Paths.``all-fun-links``, AllLinks.``all-fun-links``
    Paths.``dev-random``, Index.``dev\random``
    Paths.articles, Articles.main
    Paths.articles + "/", Articles.main
    //Paths.``portfolio-balancer``, PortfolioBalancer.``portfolio balancer``
    //Paths.``react-playground``, PortfolioBalancer.``react playground``
]
type Arguments =
    | Port of UInt16
    | HomeFolder of string
    interface IArgParserTemplate with
        member s.Usage =
            match s with
            | Port _ -> "the port to start the server listening on"
            | HomeFolder _ -> "the folder to load files from"
//let showErrorCats code = 

let customErrorHandler ex msg ctx =
    let s = ctx.response.status.code
    log.ErrorException ex "%s" msg 
    // Change implementation as you wish
    ServerErrors.INTERNAL_ERROR ("Custom error handler: " + msg) ctx
let logHit msg ctx = 
    log.Trace "%s" msg
    async { return Some ctx }

let app = 
    choose 
        [ GET >=> choose (seq {
            yield pathScan "/articles/%s" (fun x -> 
                match Articles.articles.ContainsKey x with
                | true -> Articles.articles.[x] |> renderTemplateOK
                | _ -> (fun _ -> async { return None })
            )
            for p, page in mainPages do
                yield path p >=> logHit p >=> request (fun _ -> renderTemplateOK page)
            yield path Paths.experimental >=> logHit Paths.experimental >=> Files.browseFileHome "experimental.html"
            yield pathRegex "(.*)\.(css|png|js|jpg|svg|pdf)" >=> Files.browseHome
        } |> List.ofSeq)
          POST >=> choose [
            path "/hello" >=> OK "Hello Post"
            path "/goodbye" >=> OK "Good bye Post" 
          ]
          //Suave.
          // TODO: add cutesy 404 page
          RequestErrors.NOT_FOUND "Oh snap! Looks like that page doesn't exist" >=> (fun req -> async { log.Debug "%A" req; return Some req })
        ]

[<EntryPoint>]
let main argv =
    let parser = ArgumentParser.Create<Arguments>(programName="Server.exe")
    let cliArgs = parser.Parse(argv, ignoreMissing=false, ignoreUnrecognized=true)
    let path = cliArgs.GetResult(<@ HomeFolder @>, Path.GetFullPath( Path.Combine( __SOURCE_DIRECTORY__, "..", "..", "public" ) ) )
    log.Info "%A" path 
    let cts = new CancellationTokenSource()
    let conf = { defaultConfig with 
                    errorHandler = customErrorHandler
                    cancellationToken = cts.Token; 
                    bindings = [cliArgs.GetResult(<@ Port @>, 8081us) |> HttpBinding.create HTTP IPAddress.Loopback]
                    homeFolder = Some path }
    let listening, server = startWebServerAsync conf app
    Async.Start (server, cts.Token)
    // just use concurrent queue, with blocking for backpressure 
    let p = Console.Read ()
    cts.Cancel ()
    0 // return an integer exit code 
