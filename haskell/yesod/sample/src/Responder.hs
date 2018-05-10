{-# LANGUAGE OverloadedStrings #-}
module Responder where
    import System.IO hiding (print)
    import System.Process.Typed
    import qualified Data.ByteString.Lazy as L
    import qualified Data.ByteString.Lazy.Char8 as L8
    import Control.Concurrent.STM (atomically)
    import Control.Exception
    import UnliftIO.Temporary (withSystemTempFile)
    import Options.Applicative
    import Data.Semigroup ((<>))

    data Sample = Sample
        { hello :: String
        , quiet :: Bool
        , enthusiasm :: Int }

    data Input = FileInput FilePath
        | StdInput

    fileInput :: Parser Input
    fileInput = FileInput <$> strOption
        ( long "file"
        <> short 'f')

    stdInput :: Parser Input
    stdInput = flag' StdInput
        (long "stdin")

    input :: Parser Input
    input = fileInput <|> stdInput

    data Verbosity = Normal | Verbose deriving (Eq, Show)

    verbose :: Parser Verbosity
    verbose = flag Normal Verbose
        (long "verbose"
        <> short 'v')

    sample :: Parser Sample
    sample = Sample
        <$> strOption
            ( long "hello"
            <> metavar "TARGET"
            <> help "Target for the greeting")
        <*> switch
            ( long "quiet"
            <> short 'q'
            <> help "Whether to be quiet")
        <*> option auto
            ( long "enthusiasm"
            <> help "How enthusiasticly to greet"
            <> showDefault
            <> value 1
            <> metavar "INT")

    data MyCommand = 
        MySample Sample
        | Verby Verbosity

    data Options = Options
        { optCommand :: MyCommand }

    comm :: Parser MyCommand
    comm = subparser
        (  command "mySample" (info (fmap MySample sample) $ progDesc "Add a file")
        <> command "verby" (info (fmap Verby verbose) $ progDesc "make a verbose") )

    greet :: MyCommand -> IO ()
    greet (MySample s) = putStrLn $ "Hello, " ++ (hello s) ++ replicate (enthusiasm s) '!'
    greet (Verby s) = putStrLn $ show s -- putStrLn $ "Hello, " ++ h ++ replicate n '!'
    --greet _ = return ()

    main :: IO ()
    main = --putStrLn "Hello world"
        greet =<< execParser opts
        where 
            opts = info (helper <*> comm)
              ( fullDesc
                <> progDesc "Print a greeting for TARGET"
                <> header "hello - a test for optparse-applicative")
