{-# LANGUAGE OverloadedStrings #-}
module Playrough where
    import System.IO hiding (print)
    import System.Process.Typed
    import qualified Data.ByteString.Lazy as L
    import qualified Data.ByteString.Lazy.Char8 as L8
    import Control.Concurrent.STM (atomically)
    import Control.Exception
    import UnliftIO.Temporary (withSystemTempFile)

    main :: IO ()
    main = withSystemTempFile "date" $ \fp h -> do
        let dateConfig = setStdin closed
                      $ setStdout (useHandleClose h)
                      $ setStderr closed
                      $ proc "date" [""]
        runProcess_ dateConfig
        readFile fp >>= print
