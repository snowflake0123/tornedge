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

  const handleClickCreateRoom = () => {
    props.history.push('/chatRoom');
  }

  const handleClickEnterRoom = () => {
    props.history.push('/chatRoom');
  }

  const createChatRoomId = () => {
    // Get ChatRoomID
  }

  return (
    <IonPage>
      {/* Header */}
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/functions" />
          </IonButtons>
          <IonTitle>Chat</IonTitle>
        </IonToolbar>
      </IonHeader>

      {/* Content */}
      <IonContent>
        <div className="centered">
          {/* Icon */}
          <IonIcon icon={receiptSharp} className="huge-icon ion-margin-bottom"/>
          {/* Create Room Button */}
          <IonButton size="large" strong={true} onClick={() => {
            props.history.push('/chatRoom')
          }}>
            <IonIcon icon={image} className="ion-margin-end" />Create Room
            <input className="display-none" type="file" ref={inputPhotoRef} accept="image/*" />
          </IonButton>
          {/* Enter Room Button */}
          <IonButton size="large" strong={true} onClick={() => {
            props.history.push('/chatRoom')
          }}>
            <IonIcon icon={image} className="ion-margin-end" />Enter Room
            <input className="display-none" type="file" ref={inputPhotoRef} accept="image/*" />
          </IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};
export default ChatTop;