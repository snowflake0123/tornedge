import {
  IonBackButton,
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonIcon,
  IonPage,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React from 'react';
import { RouteComponentProps } from 'react-router-dom'
import './ChatTop.css';
import { receiptSharp, image } from 'ionicons/icons';

const ChatTop: React.FC<RouteComponentProps> = (props) => {
  const inputPhotoRef = React.useRef<HTMLInputElement>(null);
  const handleClickPhoto = () => {
    if(inputPhotoRef && inputPhotoRef.current) {
      inputPhotoRef.current.click();
    }
  }

  const createRandomId = () => {

  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/functions" />
          </IonButtons>
          <IonTitle>Chat</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <div className="centered">
          <IonIcon icon={receiptSharp} className="huge-icon ion-margin-bottom"/>
          <IonButton size="large" strong={true} onClick={() => {

                                                                  props.history.push('/chatRoom')
                                                                }}>
            <IonIcon icon={image} className="ion-margin-end" />Choose Photo
            <input className="display-none" type="file" ref={inputPhotoRef} accept="image/*" />
          </IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default ChatTop;