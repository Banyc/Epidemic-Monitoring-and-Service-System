import React from 'react';
import { StyleSheet, Text, View, Button,TouchableOpacity } from 'react-native';
//import ViewPager from '@react-native-community/viewpager';
import { CheckBox,Image,Input} from 'react-native-elements';
var axios = require('axios');
//const ip="http://localhost:8000"
var ip=require('./ip')
export default class ChangeAddress extends React.Component {
  

 constructor(props){
        super(props)
        this.state = (
          {   username :this.props.navigation.getParam( 'username', 'No username provided' ),
              token :this.props.navigation.getParam( 'token', 'No token provided' ),
              address:''
          })
        //this.loginget = this.loginget.bind(this)
    }
    address='';

  change = () => {
        
         var data={
            'username': this.state.username,
            'attr':'address',
            'changevalue':this.state.address,
           }
          var token={
            'token':this.state.token,
         } 
        if(this.state.address.length>0){
        axios.post(ip+'/request/info/personalUserInfo/update', data,{headers:token}) 
        .then((res) => { //alert(JSON.stringify(res.data));
            if(res.data.result=='Y'){
               alert('修改成功!')
                 const {navigate,goBack,state} = this.props.navigation;
                state.params.callback(this.state.address);
                this.props.navigation.goBack(); 
             }
             else if(res.data.result=='L'){
              alert('令牌过期，请重新登录!') 
              const { navigate } = this.props.navigation;  
              navigate('Home');
             }
            else
               alert('修改失败!') 
                })
        .catch((error) => { console.log(error) });
        }
        else{
          alert('请检查是否有未填项')
        }
    } 

  render() {

  // const username = this.props.navigation.getParam( 'username', 'No username provided' )
    return (
      
      <View style={styles.container}>
      
        <Input
             placeholder="新地址"
             label='新地址'
             //leftIcon={{ type: 'font-awesome', name: 'address-book' }}
             style={styles}
             onChangeText={value => this.state.address=value}
            /> 

           <TouchableOpacity style={styles.button}  onPress={ this.change } >
              <Text style={styles.buttonText}> 提交 </Text>
           </TouchableOpacity> 

         
      </View>
    );
  }
  
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'stretch',
    justifyContent: 'center',
  },
  columncontainer: {
    flex: 2,
    flexDirection: 'column',
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  button: {
    margin: 20,
    padding: 10,
    paddingLeft: 20,
    paddingRight: 20,
    backgroundColor: '#4d80e6',
    borderRadius: 9,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
});
