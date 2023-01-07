o	solicitado	é implementar um servidor IRC autônomo. Para tal, deve-se assumir que existe apenas	um servidor IRC e todos os clientes estão conectados a esse servidor. 
As definições para	esse	servidor são	as	seguintes
nodeID  - identificador único que identifica um servidor IRC, ou nó. O nodeID para	
o servidor IRC independente deve ser 1.
destino – apelido ou canal de IRC como uma	cadeia de caracteres terminada em nulo. De acordo com o RFC do IRC,	os destinos terão no máximo 9 caracteres e não podem conter espaços.
Porta IRC – A porta TCP no servidor IRC que se comunica com os clientes.
O servidor deve ser capaz de suportar vários clientes simultaneamente.
Enquanto	o servidor espera que um cliente envie o próximo comando, ele deve ser capaz de lidar com as entradas de outros clientes.
O	servidor a ser desenvolvido deve implementar um subconjunto do protocolo IRC original. O protocolo IRC original é definido no RFC 1459