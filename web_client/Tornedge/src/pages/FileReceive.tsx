import {
  IonAlert,
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
  IonLoading,
  IonPage,
  IonProgressBar,
  IonTitle,
  IonToast,
  IonToolbar,
  useIonViewWillLeave
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

  const [showAlert, setShowAlert] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  const [showProgressBar, setShowProgressBar] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [showFailureToast, setShowFailureToast] = useState(false);

  const handleClickReceive = (event: React.MouseEvent<HTMLIonButtonElement>) => {
    const imageID = localStorage.getItem("image_id")
    const formData = generateFormData("cmd", "download_file",
                                      "image_id", imageID);
    setShowLoading(true);
    setShowProgressBar(true);
    axios.post("http://localhost:56060", formData).then((response) => {
      console.log('body:', response.data);
      const fPath = response.data['data']['file_path'];
      setFilePath(fPath);
      setFileName(path.basename(fPath));
      setFileExists(true);
      setShowProgressBar(false);
      setShowLoading(false);
      setShowSuccessToast(true);
    }).catch((error) => {
      console.log(error);
      setShowProgressBar(false);
      setShowLoading(false);
      setShowFailureToast(true);
    });
  };

  useIonViewWillLeave(() => {
    setShowAlert(false);
    setShowProgressBar(false);
    setShowSuccessToast(false);
    setShowFailureToast(false);
  });

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

        <IonLoading
          isOpen={showLoading}
          message={'Downloading...'}
        />
        <IonProgressBar type="indeterminate" reversed={true} style={{ display: showProgressBar ? '' : 'none' }}></IonProgressBar>
        <IonToast
          isOpen={showSuccessToast}
          color="primary"
          position="middle"
          onDidDismiss={() => setShowSuccessToast(false)}
          message="File Download Succeeded."
          duration={2500}
        />
        <IonToast
          isOpen={showFailureToast}
          color="danger"
          position="middle"
          onDidDismiss={() => setShowFailureToast(false)}
          message="File Download Failed."
          duration={2500}
        />
        <IonAlert
          isOpen={showAlert}
          onDidDismiss={() => setShowAlert(false)}
          header={'Are you sure you want to receive the file?'}
          buttons={[
            { text: 'Cancel', role: 'cancel' },
            { text: 'Receive File', handler: handleClickReceive }
          ]}
        />

        <div className="footer-button">
          <IonButton expand="full" size="large" className="ion-align-self-end" onClick={() => setShowAlert(true)} >Receive</IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default FileReceive;
