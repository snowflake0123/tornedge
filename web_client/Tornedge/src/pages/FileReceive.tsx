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
  IonPage,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React, { useState } from 'react';
import './FileReceive.css';
import { document } from 'ionicons/icons';
import axios from 'axios';
import { generateFormData } from './../generateFormData';

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
    // axios.post("http://localhost:56060", formData).then((response) => {
    //   console.log('body:', response.data);
    //   const fPath = "responceのfile_path";
    //   setFilePath(fPath);
    //   setFileName(path.basename(fPath));
    //   setFileExists(true);
    // }).catch((error) => {
    //   console.log(error);
    // });

    // ----- For debug only. -----
    // const fPath = "./../../../../app/simulator/default.jpg";
    // setFilePath(fPath);
    // setFileName(path.basename(fPath));
    // setFileExists(true);
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
              <div style={{ display: fileExists ? '' : 'none' }}>
                <IonIcon icon={document} />
                <a href={filePath}>{fileName}</a>
              </div>
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
