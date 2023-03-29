import React from 'react'
import Uppy from '@uppy/core'
import { Dashboard } from '@uppy/react'
import StatusBar from '@uppy/status-bar'

const uppy = new Uppy({
  meta: { type: 'avatar' },
  restrictions: { maxNumberOfFiles: 1 },
  autoProceed: true
})

uppy.use(StatusBar)

uppy.on('file-added', (file) => {
  const reader = new FileReader()
  if (file) {
    reader.readAsDataURL(file.data)
    const fileName = file.name
    const fileType = file.type
    reader.onloadend = () => {
      const base64data = reader.result
      console.log(base64data, fileName, fileType)
    }
  }
})

export const Uploader = () => {
  return (
    <Dashboard
      uppy={uppy}
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
  )
}
