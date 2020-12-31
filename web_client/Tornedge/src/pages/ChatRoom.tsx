import {
  IonBackButton,
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonIcon,
  IonItem,
  IonLabel,
  IonList,
  IonPage,
  IonRefresher,
  IonRefresherContent,
  IonTextarea,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React from 'react';
import './ChatRoom.css';
import { RefresherEventDetail } from '@ionic/core';
import { chevronDownCircleOutline } from 'ionicons/icons';
import { IonReactRouter } from '@ionic/react-router';
import { RouteComponentProps } from 'react-router';

function doRefresh(event: CustomEvent<RefresherEventDetail>) {
  console.log('Begin async operation');

  setTimeout(() => {
    console.log('Async operation has ended');
    event.detail.complete();
  }, 1000);
}

type Message = {
  who: string
  text: string
}

type Messages = {
  messages: Message[]
}

const testMessages: Message[] = [
  {
    who: "me",
    text: "Hi, we met earlier. I'm Bob."
  },
  {
    who: "partner",
    text: "Hey Bob. I'm Kenny."
  },
  {
    who: "me",
    text: "I'd like to continue what we were talking about earlier, if that's okay."
  },
  {
    who: "partner",
    text: "Of course."
  },
  {
    who: "partner",
    text: "Oh, I'm sorry. I've got some business to attend to later, so can I have ten minutes with you?"
  },
  {
    who: "me",
    text: "Okay! Then let's talk briefly."
  },
]

const MyMsg: React.FC<Message> = (props) => {
  return (
    <IonItem lines="none">
      <IonLabel className="ion-margin-start me-speech-bubble ion-padding ion-text-wrap">
        {props.text}
      </IonLabel>
    </IonItem>
  )
}

const PartnerMsg: React.FC<Message> = (props) => {
  return (
    <IonItem lines="none">
      <IonLabel className="ion-margin-end partner-speech-bubble ion-padding ion-text-wrap">
        {props.text}
      </IonLabel>
    </IonItem>
  )
}

const MsgList: React.FC<Messages> = (props) => {
  if (props.messages.length === 0) return null;
  return (
    <IonList className="ion-padding-top">
      { props.messages.map((message: Message, index:number) => {
        if (message.who === "me") {
          return (<MyMsg key={index} who={message.who} text={message.text}/>)
        } else {
          return (<PartnerMsg key={index} who={message.who} text={message.text}/>)
        }
      })}
    </IonList>
  )
}


const ChatRoom: React.FC<RouteComponentProps> = (props) => {
  
  const handleClickBack = () => {
    props.history.goBack();
    // Function
    //   Step1: Send ID and command
    //   Step2: Change ID's chatflag data to false
  }

  return (
    <IonPage>
      {/* Header */}
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonButton fill="clear" size="small" onClick={() => handleClickBack()}>Back</IonButton>
          </IonButtons>
          <IonTitle>Chat -Chat Room-</IonTitle>
          {/* Send Button */}
          <IonButtons slot="end">
            <IonButton fill="clear" size="small">Send</IonButton>
          </IonButtons>
        </IonToolbar>
        <IonToolbar color="primary" style={{padding:"4px 8px"}}>
          {/* Input Form */}
          <form>
            <IonTextarea className="ion-margin-start" autoGrow={true} rows={1} placeholder="Message" name="message" required></IonTextarea>
          </form>
        </IonToolbar>
      </IonHeader>

      {/* Chat Space */}
      <IonContent>
        <IonRefresher slot="fixed" onIonRefresh={doRefresh}>
          <IonRefresherContent
            pullingIcon={chevronDownCircleOutline}
            pullingText="Pull to refresh"
            refreshingSpinner="circles"
            refreshingText="Refreshing...">
          </IonRefresherContent>
        </IonRefresher>
        <MsgList messages={testMessages} />
      </IonContent>

    </IonPage>
  );
};
export default ChatRoom;