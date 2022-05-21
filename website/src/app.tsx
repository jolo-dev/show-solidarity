import Uppy from '@uppy/core'
import AwsS3 from '@uppy/aws-s3'
import { DragDrop, useUppy, StatusBar } from '@uppy/react'
// import { uploadImage } from './s3client'


import '@uppy/core/dist/style.css'
import '@uppy/drag-drop/dist/style.css'

const bucketName = import.meta.env.VITE_SOURCE_BUCKET_NAME
const resultBucketName = import.meta.env.VITE_RESULT_BUCKET_NAME

// const blobToBase64 = ( blob: Blob | File ) => new Promise<string>( ( resolve, reject ) => {
//   const reader = new FileReader();
//   reader.readAsDataURL( blob );
//   reader.onload = () => ( typeof reader.result === 'string' ) ? resolve( reader.result ) : undefined
//   reader.onerror = error => reject( error );
// } );

export function App() {
  const uppy = useUppy( () => {
    return new Uppy( { id: 'uppy', autoProceed: true, debug: true } ).use( AwsS3, {
      id: 'AWS S3 Target',
      timeout: 600,
      getUploadParameters: async ( file ) => {
        // const base64Encoded = await blobToBase64( file.data )
        // const body = base64Encoded.split( ',' )[1]; // to remove the prefix (data type)

        const api = await fetch( 'https://s6bwnumkv1.execute-api.eu-central-1.amazonaws.com/prod', {
          method: 'post',
          headers: {
            accept: 'application/json',
            'content-type': 'application/json',
          },
          body: JSON.stringify( {
            key: file.name,
            contentType: file.type,
            // body,
            bucketName,
            resultBucketName
          } ),
        } )
        return {
          url: api.url
        }
      },
    } ).on( 'file-added', async ( file ) => {
      const reader = new FileReader();
      if ( file ) {
        reader.readAsDataURL( file.data );
        reader.onloadend = async () => {
          const base64data = reader.result;
          if ( typeof base64data === 'string' ) {
            // const response = await uploadImage( bucketName, file.name, file.data )
            // if ( response.$metadata.httpStatusCode == 200 ) {
            //   console.log( 'upload successfull' );
            // }
          }
        };
      }
    } ).on( 'upload', () => {
      console.log( 'Upload' );
    } ).on( 'progress', () => {
      console.log( 'Progress' );
    } )
  } )
  return (
    <>
      <section className="relative flex flex-wrap lg:h-screen lg:items-center">
        <div className="w-full px-4 py-12 lg:w-1/2 sm:px-6 lg:px-8 sm:py-16 lg:py-24">
          <div className="max-w-lg mx-auto text-center">
            <h1 className="text-2xl font-bold sm:text-3xl">Show Solidarity!</h1>

            <p className="mt-4 text-gray-500" >
              Show Solidarity with Ukraine to your Social Media profile picture and be against Russian aggression.
            </p >
          </div >

          <DragDrop
            width="100%"
            height="100%"
            note="Better result when at least 800×800px"
            // assuming `this.uppy` contains an Uppy instance:
            uppy={uppy}
            onDrop={() => { console.log( uppy.getFiles()[0].data ) }}
            locale={{
              strings: {
                // Text to show on the droppable area.
                // `%{browse}` is replaced with a link that opens the system file selection dialog.
                dropHereOr: 'Drop here or %{browse}',
                // Used as the label for the link that opens the system file selection dialog.
                browse: 'browse',

              },
            }}
          />

        </div >

        <div className="relative w-full h-64 sm:h-96 lg:w-1/2 lg:h-full" >
          <img
            className="absolute inset-0 w-full h-full"
            src="./assets/intro.jpeg"
            alt="peace"
          />
          <StatusBar
            uppy={uppy}
            hideUploadButton
            hideAfterFinish={false}
            showProgressDetails
          />
          Photo by <a href="https://unsplash.com/@kedar9?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText"> Kedar Gadge</a> on <a href="https://unsplash.com/s/photos/ukraine?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText" > Unsplash</a>
        </div >
      </section >
    </>
  )
}
