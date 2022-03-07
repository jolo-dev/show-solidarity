import Uppy from '@uppy/core'
import AwsS3 from '@uppy/aws-s3'
import { DragDrop, useUppy, ProgressBar } from '@uppy/react'
import { uploadImage } from './s3client'


import '@uppy/core/dist/style.css'
import '@uppy/drag-drop/dist/style.css'

const bucketName = import.meta.env.VITE_BUCKET_NAME ?? 'show-solidarity'

export function App() {
  const uppy = useUppy( () => {
    return new Uppy().use( AwsS3, {
      id: 'AWS S3 Target',
    } ).on( 'file-added', async ( file ) => {
      const reader = new FileReader();
      if ( file ) {
        reader.readAsDataURL( file.data );
        reader.onloadend = async () => {
          const base64data = reader.result;
          if ( typeof base64data === 'string' ) {
            await uploadImage( bucketName, file.name, file.data )
          }
        };
      }
    } )
  } )



  return (
    <>
      <h1>Show Solidarity 🇺🇦</h1>
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
    </>
  )
}
