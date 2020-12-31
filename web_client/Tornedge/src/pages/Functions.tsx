import { IonBackButton,
         IonButtons,
         IonCard,
         IonCardHeader,
         IonCardTitle,
         IonCardContent,
         IonContent,
         IonIcon,
         IonHeader,
         IonPage,
         IonTitle,
         IonToolbar,
       } from '@ionic/react';
import React from 'react';
import { RouteComponentProps } from 'react-router-dom'
import './Home.css';
import { chatbubbles, document } from 'ionicons/icons';

const Functions: React.FC<RouteComponentProps> = (props) => {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/home" />
          </IonButtons>
          <IonTitle>Functions</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <div className="centered">
          <div className="functions ion-align-items-center ion-justify-content-center">
            <IonCard className="ion-text-center" onClick={() => props.history.push('/fileTop')}>
              <IonCardHeader>
                <IonCardTitle>File</IonCardTitle>
              </IonCardHeader>
              <IonIcon icon={document} size="large"/>
              <IonCardContent>
                File transfer<br /> by using a piece of paper.
              </IonCardContent>
            </IonCard>

            <IonCard className="ion-text-center" onClick={() => props.history.push('/chatTop')}>
              <IonCardHeader>
                <IonCardTitle>Chat</IonCardTitle>
              </IonCardHeader>
              <IonIcon icon={chatbubbles} size="large" />
              <IonCardContent>
                Chat<br /> by using a piece of paper.
              </IonCardContent>
            </IonCard>
          </div>
        </div>
      </IonContent>
    </IonPage>
  );
};

export default Functions;
