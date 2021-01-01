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
  IonLabel,
  IonPage,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React, { useState } from 'react';
import './FileSend.css';
import { document } from 'ionicons/icons';
import axios from 'axios';
import { generateFormData } from './../generateFormData';

const FileSend: React.FC = () => {
  const inputFileRef = React.useRef<HTMLInputElement>(null);
  const handleClickFile = () => {
    if (inputFileRef && inputFileRef.current) {
      inputFileRef.current.click();
    }
  }

  const handleClickSend = (event: React.MouseEvent<HTMLIonButtonElement>) => {
    const formData = generateFormData("cmd", "upload_image",
                                      "image", fileData);
    // TODO: サーバに formData を POST する
    // axios.post("http://localhost:56060", formData).then(response => {
    //   console.log('body:', response.data);
    // });
  };

  const [fileData, setFileData] = useState<File | null>(null)
  const [fileName, setFileName] = useState("No File chosen");
  const handleChangeFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files;
    let fName = "No File chosen";
    if (file !== null && file[0] !== (null || undefined)) {
      fName = file[0].name;
      setFileData(file[0]);
    }
    setFileName(fName);
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/FileTop" />
          </IonButtons>
          <IonTitle>File -Send-</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <IonCard>
          <IonCardHeader>
            <IonCardTitle>File</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <IonButton size="large" strong={true} onClick={handleClickFile}>
              <IonIcon icon={document} className="ion-margin-end" />Choose File
              <input name="file" className="display-none" type="file" onChange={handleChangeFile} ref={inputFileRef} />
            </IonButton>
            <br />
            <IonLabel className="ion-margin">{fileName}</IonLabel>
          </IonCardContent>
        </IonCard>
        <div className="footer-button">
          <IonButton expand="full" size="large" className="ion-align-self-end" onClick={handleClickSend}>Send</IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default FileSend;
