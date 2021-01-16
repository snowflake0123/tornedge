import {
  IonBackButton,
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
import React from 'react';
import { RouteComponentProps } from 'react-router-dom'
import './FileTop.css';
import { cloudUpload, cloudDownload } from 'ionicons/icons';

const FileTop: React.FC<RouteComponentProps> = (props) => {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/functions" />
          </IonButtons>
          <IonTitle>File</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <div className="centered">
          <div className="roles">
            <IonCard className="role ion-text-center" onClick={() => props.history.push('/fileSend')}>
              <IonCardHeader>
                <IonCardTitle className="ion-text-nowrap">Send</IonCardTitle>
              </IonCardHeader>
              <IonIcon icon={cloudUpload} className="larger-icon" />
              <IonCardContent>
              </IonCardContent>
            </IonCard>

            <IonCard className="role ion-text-center" onClick={() => props.history.push('/fileReceive')}>
              <IonCardHeader>
                <IonCardTitle className="ion-text-nowrap">Receive</IonCardTitle>
              </IonCardHeader>
              <IonIcon icon={cloudDownload} className="larger-icon" />
              <IonCardContent>
              </IonCardContent>
            </IonCard>
          </div>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default FileTop;
