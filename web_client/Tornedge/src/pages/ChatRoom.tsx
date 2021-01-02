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
  IonToast
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
  const [showToast, setShowToast] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')  

  const handleClickBack = () => {
    console.log('[API] exit_chat');
   /* Function
    *   Step1: Send request
    *   Step2: clear chat log data in state
    *   Step3: back to ChatTop page
    */   

    // 1: send request
    const formData = generateFormData(
      'cmd', 'exit_chat',
      'image_id', '1'
    )
    axios.post('http://localhost:56060', formData).then((response) => {
      // 2: clear chat log data in state
      const res: string = response.data.data.result
      if(res == 'success') {
        setMessages([]);
      } else {
        setErrorMessage(response.data.data.message);
        setShowToast(true);
      }
    })
    .catch((error) => {
      console.log(error);
    })
    // 3: back to ChatTop page
    props.history.goBack(); 
  }


  const handleClickSend = () => {
   /* Functions
    *   Step1: Send request
    *   Step2: Update chat log value in state
    *   Step3: Reset value of input textarea
    */
    console.log('[API] send_chat');
    
    // 1: send request
    const formData = generateFormData(
      'cmd', 'send_chat',
      'message', message,
      'chat_room_id', localStorage.getItem('chat_room_id')
    );
    axios.post('http://localhost:56060', formData).then((response) => {
      // 2: update chat log value in state
      if(response.data.data.result === 'success') {
        setMessages(response.data.data.chat_log);
      } else {
        setErrorMessage(response.data.data.message);
        setShowToast(true);
      }
    })
    // 3: Reset value of input textarea
    setMessage('');
  }


  const handleClickUpdate = () => {
   /* Functions
    *   Step1: Send request
    *   Step2: Update chat log value in state
    */
    console.log('[API] update_chat');
    // 1: send request
    const formData = generateFormData(
      'cmd', 'update_chat',
      'chat_room_id', localStorage.getItem('chat_room_id')
    )
    axios.post('http:/localhost:56060', formData).then((response) => {
      // 2: update chat log value in state
      if(response.data.data.reslut == 'success') {
        setMessages(response.data.data.chat_log);
      } else {
        setErrorMessage(response.data.data.message);
        setShowToast(true);
      }
    })
    .catch((error) => {
      console.log(error);
    })
  }

  useIonViewWillEnter(() => handleClickUpdate())

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

      {/* Toast */}
      <IonToast
        isOpen={showToast}
        onDidDismiss={() => setShowToast(false)}
        message={errorMessage}
        duration={200}
      />

    </IonPage>
  );
};
export default ChatRoom;