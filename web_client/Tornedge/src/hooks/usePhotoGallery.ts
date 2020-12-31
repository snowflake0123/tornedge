import { useState, useEffect } from "react";
import { useCamera } from '@ionic/react-hooks/camera';
import { useFilesystem, base64FromPath } from '@ionic/react-hooks/filesystem';
import { useStorage } from '@ionic/react-hooks/storage';
import { isPlatform } from '@ionic/react';
import { CameraResultType, CameraSource, CameraPhoto, Capacitor, FilesystemDirectory } from "@capacitor/core";

export interface Photo {
  filepath: string;
  webviewPath?: string;
}

export function usePhotoGallery() {

  const { getPhoto } = useCamera();
  const [photo, setPhoto] = useState<Photo>();

  const takePhoto = async () => {
    const cameraPhoto = await getPhoto({
      resultType: CameraResultType.Uri,
      source: CameraSource.Camera,
      quality: 100
    });
    const fileName = new Date().getTime() + '.jpeg';
    const takenPhoto = {
      filepath: fileName,
      webviewPath: cameraPhoto.webPath
    };
    setPhoto(takenPhoto)
  };

  return {
  	photo,
    takePhoto
  };
}