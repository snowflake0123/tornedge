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
  IonToolbar,
  useIonViewWillEnter,
  IonInput,
} from '@ionic/react';
import React, { useState } from 'react';
import './ChatRoom.css';
import { RefresherEventDetail } from '@ionic/core';
import { chevronDownCircleOutline, reload } from 'ionicons/icons';
import { IonReactRouter } from '@ionic/react-router';
import { RouteComponentProps } from 'react-router';
import axios from 'axios';
import { convertCompilerOptionsFromJson, setConstantValue } from 'typescript';
import { generateFormData } from '../generateFormData';

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
  const [messages, setMessages] = useState(testMessages)
  const [message, setMessage] = useState('')
  
  const handleClickBack = () => {
    console.log('[API] exit_chat');
    // Function
    //   Step1: Send ID and command
    //   Step2: Change ID's chatflag data to false
    const formData = generateFormData(
      'cmd', 'exit_chat',
      'image_id', '1'
    )

    axios.post('http://localhost:56060', formData).then((response) => {
      console.log(response);
    })
    .catch((error) => {
      console.log(error);
    })

    props.history.goBack(); 
  }

  const handleClickSend = () => {
    console.log('[API] send_chat');

    const formData = generateFormData(
      'cmd', 'send_chat',
      'message', message,
      'chat_room_id', localStorage.getItem('chat_room_id')
    );

    axios.post('http://localhost:56060', formData).then((respose) => {
      setMessages(respose.data.data.chat_log);
    })
    setMessage('');
  }

  const handleClickUpdate = () => {
    console.log('[API] update_chat');
  }

  useIonViewWillEnter(() => {
    console.log('[API] enter_chat_room')

    const formData = new FormData();
    formData.append('cmd', 'enter_chat_room');
    formData.append('image_id', '1');

    axios.post('http://localhost:56060', formData).then((response) => {
      console.log(response.data);
    })
    .catch((error) => {
      console.log(error);
    });
    
  })

  return (
    <IonPage>
      {/* Header */}
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonButton fill="clear" size="small" onClick={() => handleClickBack()}>Back</IonButton>
          </IonButtons>
          <IonTitle>Chat -Chat Room-</IonTitle>
          {/* Reload Button */}
          <IonButton slot="end" color="midium" size="small" onClick={() => handleClickUpdate()}>
            <IonIcon icon={reload}></IonIcon>
          </IonButton>
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
        <MsgList messages={messages} />
      </IonContent>

      {/* Input */}
      <IonItem>
        <IonInput
          className="ion-margin-start" 
          color="Midium" 
          placeholder="Message" 
          value={message}
          onIonChange={e => setMessage(e.detail.value!)}
          required
          >
        </IonInput>
      </IonItem>
      <div className="ion-padding">
        <IonButton color="success" expand="block" onClick={() => handleClickSend()}>Send</IonButton>
      </div>



    </IonPage>
  );
};
export default ChatRoom;