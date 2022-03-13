import Uppy from '@uppy/core'
import AwsS3 from '@uppy/aws-s3'
import { DragDrop, useUppy, StatusBar } from '@uppy/react'
import { uploadImage } from './s3client'


import '@uppy/core/dist/style.css'
import '@uppy/drag-drop/dist/style.css'

const bucketName = import.meta.env.VITE_BUCKET_NAME ?? 'show-solidarity'

export function App() {
  const uppy = useUppy( () => {
    return new Uppy( { id: 'uppy', autoProceed: true, debug: true } ).use( AwsS3, {
      id: 'AWS S3 Target',
      getUploadParameters: async ( file ) => {
        console.log( file );

        const data = await fetch( 'foo.bar', {
          method: 'post',
          headers: {
            accept: 'application/json',
            'content-type': 'application/json',
          },
          body: JSON.stringify( {
            filename: file.name,
            contentType: file.type,
            data: file.data
          } ),
        } )
        return {
          url: data.url
        }
      },
    } ).on( 'file-added', async ( file ) => {
      const reader = new FileReader();
      if ( file ) {
        reader.readAsDataURL( file.data );
        reader.onloadend = async () => {
          const base64data = reader.result;
          if ( typeof base64data === 'string' ) {
            const response = await uploadImage( bucketName, file.name, file.data )
            if ( response.$metadata.httpStatusCode == 200 ) {
              console.log( 'upload successfull' );
            }
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
      <h1>Show Solidarity 🇺🇦</h1>
      <img width={400} src='./assets/intro.jpeg' />
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
      <StatusBar
        uppy={uppy}
        hideUploadButton
        hideAfterFinish={false}
        showProgressDetails
      />
      Photo by <a href="https://unsplash.com/@kedar9?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Kedar Gadge</a> on <a href="https://unsplash.com/s/photos/ukraine?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
    </>
  )
}
