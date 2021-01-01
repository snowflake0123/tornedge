import {
  IonBackButton,
  IonButton,
  IonButtons,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonContent,
  IonHeader,
  IonIcon,
  IonItem,
  IonItemOption,
  IonItemOptions,
  IonItemSliding,
  IonLabel,
  IonList,
  IonListHeader,
  IonPage,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React, { useState } from 'react';
import './FileReceive.css';
import { document } from 'ionicons/icons';
import axios from 'axios';
import useLocalStorage from './../hooks/useLocalStorage'
import { generateFormData } from './../generateFormData';

const ReceivedFile: React.FC = () => {
  return (
    <IonItemSliding>
      <IonItem href="https://www.google.com">
        <IonLabel>Item</IonLabel>
      </IonItem>
      <IonItemOptions side="end">
        <IonItemOption color="danger" onClick={() => { }}>Delete</IonItemOption>
      </IonItemOptions>
    </IonItemSliding>
  )
}

const FileReceive: React.FC = () => {
  const path = require('path');
  const [fileExists, setFileExists] = useState<boolean>(false);
  const [filePath, setFilePath] = useState<string>("")
  const [fileName, setFileName] = useState<string>("")

  const handleClickReceive = (event: React.MouseEvent<HTMLIonButtonElement>) => {
    const imageID = localStorage.getItem("image_id")
    const formData = generateFormData("cmd", "download_file",
                                      "image_id", imageID);
    // TODO: サーバに formData を POST する
    // axios.post("http://localhost:56060", formData).then(response => {
    //   console.log('body:', response.data);
    //   const fPath = "responceのfile_path";
    //   setFilePath(fPath);
    //   setFileName(path.basename(fPath));
    //   setFileExists(true);
    // });
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/FileTop" />
          </IonButtons>
          <IonTitle>File -Receive-</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <div className="centered-card">
          <IonCard>
            <IonCardHeader>
              <IonCardTitle>Received File</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <div style={{ display: fileExists ? 'none' : '' }}>No file received</div>
              <a style={{ display: fileExists ? '' : 'none' }} href={filePath}>{fileName}</a>
            </IonCardContent>
          </IonCard>
        </div>
        <div className="footer-button">
          <IonButton expand="full" size="large" className="ion-align-self-end" onClick={handleClickReceive} >Receive</IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default FileReceive;
