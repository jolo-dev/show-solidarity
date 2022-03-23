/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_AWS_REGION: string
    readonly VITE_SOURCE_BUCKET_NAME: string
    readonly VITE_RESULT_BUCKET_NAME: string
    readonly VITE_AWS_ACCESS_KEY_ID: string
    readonly VITE_AWS_SECRET_ACCESS_KEY: string
    readonly VITE_AWS_SESSION_TOKEN?: string
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }