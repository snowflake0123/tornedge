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
  IonPage,
  IonTitle,
  IonToolbar
} from '@ionic/react';
import React from 'react';
import './FileSend.css';
import { document, images } from 'ionicons/icons';
import { useForm } from 'react-hook-form';
import axios from 'axios';

type Inputs = {
  type: string;
  receipt: FileList;
  file: FileList;
};

const FileSend: React.FC = () => {
  const { register, setValue, handleSubmit } = useForm<Inputs>();

  const onSubmit = (data: Inputs) => {
    console.log("data", data);
    // axios.post("http://localhost:56060/", data).then(response => {
    //   console.log('body:', response.data);
    // });
  };

  const setTypeSender = () => {
    setValue("type", "sender");
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
        <form onSubmit={handleSubmit(onSubmit)}>
          <input name="type" className="display-none" type="text" ref={register} />
          {/*<IonCard>
            <IonCardHeader>
              <IonCardTitle>A Piece of Paper</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <label className="choose-button" onClick={setTypeSender}>
                <IonIcon icon={images} className="ion-margin-end" />Choose Photo
                <input name="receipt" className="display-none" type="file" ref={register({required: true})} accept="image/*" />
              </label>
            </IonCardContent>
          </IonCard>*/}
          <IonCard>
            <IonCardHeader>
              <IonCardTitle>File</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <label className="choose-button" onClick={setTypeSender}>
                <IonIcon icon={document} className="ion-margin-end" />Choose File
                <input name="file" className="display-none" type="file" ref={register({required: true})} />
              </label>
            </IonCardContent>
          </IonCard>
          <div className="footer-button">
            <IonButton expand="full" size="large" className="ion-align-self-end" type="submit">Send</IonButton>
          </div>
        </form>
      </IonContent>
    </IonPage>
  );
};
export default FileSend;