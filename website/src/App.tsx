import Uppy from '@uppy/core'
import AwsS3 from '@uppy/aws-s3'
import { DragDrop, useUppy, StatusBar } from '@uppy/react'
// import { uploadImage } from './s3client'

import '@uppy/core/dist/style.css'
import '@uppy/drag-drop/dist/style.css'

const bucketName = import.meta.env.VITE_SOURCE_BUCKET_NAME
const resultBucketName = import.meta.env.VITE_RESULT_BUCKET_NAME

export function App() {
  const uppy = useUppy(() => {
    return new Uppy({ id: 'uppy', autoProceed: true, debug: true })
      .use(AwsS3, {
        id: 'AWS S3 Target',
        timeout: 600
      })
      .on('file-added', async (file) => {
        console.log('file-added')

        const reader = new FileReader()
        if (file) {
          reader.readAsDataURL(file.data)

          reader.onloadend = async () => {
            const base64data = reader.result
            console.log(base64data)
            if (typeof base64data === 'string') {
              const api = await fetch(
                'https://7vjxthsxif.execute-api.eu-central-1.amazonaws.com/prod',
                {
                  method: 'post',
                  headers: {
                    accept: 'application/json',
                    'content-type': 'application/json'
                  },
                  body: JSON.stringify({
                    key: file.name,
                    contentType: file.type,
                    body: base64data,
                    bucketName,
                    resultBucketName
                  })
                }
              )
            }
          }
        }
      })
      .on('upload', (file) => {
        console.log('Upload', file)
      })
      .on('progress', () => {
        console.log('Progress')
      })
  })
  return (
    <>
      <section className='relative flex flex-wrap lg:h-screen lg:items-center'>
        <div className='w-full px-4 py-12 lg:w-1/2 sm:px-6 lg:px-8 sm:py-16 lg:py-24'>
          <div className='max-w-lg mx-auto text-center'>
            <h1 className='text-2xl font-bold sm:text-3xl'>Show Solidarity!</h1>

            <p className='mt-4 text-gray-500'>
              Show Solidarity with Ukraine to your Social Media profile picture
              and be against Russian aggression.
            </p>
          </div>

          <DragDrop
            width='100%'
            height='100%'
            note='Better result when at least 800×800px'
            // assuming `this.uppy` contains an Uppy instance:
            uppy={uppy}
            onDrop={() => {
              console.log(uppy.getFiles()[0].data)
            }}
            locale={{
              strings: {
                // Text to show on the droppable area.
                // `%{browse}` is replaced with a link that opens the system file selection dialog.
                dropHereOr: 'Drop here or %{browse}',
                // Used as the label for the link that opens the system file selection dialog.
                browse: 'browse'
              }
            }}
          />
        </div>

        <div className='relative w-full h-64 sm:h-96 lg:w-1/2 lg:h-full'>
          <img
            className='absolute inset-0 w-full h-full'
            src='./intro.jpeg'
            alt='peace'
          />
          <StatusBar
            uppy={uppy}
            hideUploadButton
            hideAfterFinish={false}
            showProgressDetails
          />
          Photo by{' '}
          <a href='https://unsplash.com/@kedar9?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText'>
            {' '}
            Kedar Gadge
          </a>{' '}
          on{' '}
          <a href='https://unsplash.com/s/photos/ukraine?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText'>
            {' '}
            Unsplash
          </a>
        </div>
      </section>
    </>
  )
}
