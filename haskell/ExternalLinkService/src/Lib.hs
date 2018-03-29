{-# LANGUAGE OverloadedStrings #-}
module Lib
    ( someFunc
    ) where
import qualified Data.Text.IO as T
import Acme.Missiles
someFunc :: IO ()
someFunc = do
    T.putStrLn ""
    T.putStrLn "Hello World!"
    launchMissiles
