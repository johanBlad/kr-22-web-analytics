import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as DataSink from '../lib/data-sink-stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new DataSink.DataSinkStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT));
});
