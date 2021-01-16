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
  IonLabel,
  IonLoading,
  IonPage,
  IonProgressBar,
  IonTitle,
  IonToast,
  IonToolbar,
  useIonViewWillLeave,
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

  const [showAlert, setShowAlert] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  const [showProgressBar, setShowProgressBar] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [showFailureToast, setShowFailureToast] = useState(false);

  const handleClickSend = (event: React.MouseEvent<HTMLIonButtonElement>) => {
    const imageID = localStorage.getItem("image_id")
    const formData = generateFormData("cmd", "upload_file",
                                      "image_id", imageID,
                                      "file", fileData);
    setShowLoading(true);
    setShowProgressBar(true);
    axios.post("http://localhost:56060", formData).then((response) => {
      console.log('body:', response.data);
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

        <IonLoading
          isOpen={showLoading}
          message={'Uploading...'}
        />
        <IonProgressBar type="indeterminate" style={{ display: showProgressBar ? '' : 'none' }}></IonProgressBar>
        <IonToast
          isOpen={showSuccessToast}
          color="primary"
          position="middle"
          onDidDismiss={() => setShowSuccessToast(false)}
          message="File Upload Succeeded."
          duration={2500}
        />
        <IonToast
          isOpen={showFailureToast}
          color="danger"
          position="middle"
          onDidDismiss={() => setShowFailureToast(false)}
          message="File Upload Failed."
          duration={2500}
        />
        <IonAlert
          isOpen={showAlert}
          onDidDismiss={() => setShowAlert(false)}
          header={'Are you sure you want to send the file?'}
          buttons={[
            { text: 'Cancel', role: 'cancel' },
            { text: 'Send File', handler: handleClickSend }
          ]}
        />

        <div className="footer-button">
          <IonButton expand="full" size="large" className="ion-align-self-end" onClick={() => setShowAlert(true)}>Send</IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default FileSend;
